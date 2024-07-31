/** @odoo-module **/
import { patch } from "web.utils";
import { X2ManyFieldDialog } from "@web/views/fields/relational_utils";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

patch(X2ManyFieldDialog.prototype, "hr_face_recognition_pro", {
  /**
   * Dirty patching of the 'X2ManyFieldDialog'.
   * It is done to force the "save and new" to close the dialog first, and then click again on
   * the "Add a line" link.
   *
   * This is the only way (or at least the least complicated) to correctly compute the sequence
   * field, which is crucial when creating chatbot.steps, as they depend on each other.
   *
   */
  setup() {
    this._super(...arguments);
    console.log(this, "kanban");
    this.rpc = useService("rpc");
  },

  async save({ saveAndNew }) {
    if (
      this.record.resModel !== "res.users.image" &&
      this.record.resModel !== "hr.employee.image"
    ) {
      return this._super(...arguments);
    }

    if (await this.record.checkValidity()) {
      await this.load_models();
      const image = $("#face-recognition-image img")[0];
      let res = await this._detectFaceFromImageBase64(image);
      if (res.error) {
        Swal.close();
        Swal.fire({
          title: "Ooops",
          html: "Dont found face on image, please select other or crop face manually",
          icon: "warning",
        });
        return;
      }
      this.record.data.descriptor = res.descriptorBase64;
      this.record.data.image_detection = res.imageDescriptorBase64;

      await this._create_image(this.record);
      // this.record = (await this.props.save(this.record, { saveAndNew })) || this.record;
      if (!saveAndNew) location.reload();
      Swal.close();
    } else {
      return false;
    }

    if (saveAndNew) {
      document.querySelector("button.o-kanban-button-new").click();
    }
    this.props.close();

    return true;
  },

  async _detectFaceFromImageBase64(image) {
    const result = await this.human.detect(image);

    if (!result.face.length)
      return {
        descriptorBase64: false,
        imageDescriptorBase64: false,
        error: "Not found faces",
      };

    let imageDescriptorBase64 = await this._drawDescriptor(image, result);
    let descriptorBase64 = this._f32base64(result.face[0].embedding);

    return {
      descriptorBase64: descriptorBase64,
      imageDescriptorBase64: imageDescriptorBase64.split(",")[1],
      error: false,
    };
  },

  async load_models() {
    let def = $.Deferred();
    if (!this.human) {
      const myConfig = {
        debug: false,
        async: true,
        backend: session.face_recognition_pro_backend || "humangl",
        modelBasePath:
          "/hr_attendance_face_recognition_pro/static/src/js/models",
        face: {
          // runs all face models
          face: { enabled: true },
          mesh: { enabled: true },
          description: { enabled: true },
          detector: { rotation: false },
          iris: { enabled: false },
          emotion: { enabled: false },
        },
        hand: { enabled: false },
        body: { enabled: false },
        object: { enabled: false },
        gesture: { enabled: false },
        segmentation: { enabled: false },
        filter: { enabled: false },
      };
      this.human = new Human.Human(myConfig);
      await this.human.load();
    }
    def.resolve();
    return def;
  },

  // _progressbar (record, func) {
  //     return Swal.fire({
  //         title: 'Face descriptor create process...',
  //         html: 'I will close in automaticaly',
  //         timerProgressBar: true,
  //         allowOutsideClick: false,
  //         showCloseButton: false,
  //         showConfirmButton: false,
  //         showClass: {
  //             popup: 'animate__animated animate__fadeInDown'
  //           },
  //           hideClass: {
  //             popup: 'animate__animated animate__fadeOutUp'
  //           },
  //         icon: "info",
  //         backdrop: `
  //         rgba(0,0,123,0.0)
  //         url("/auth_faceid/static/description/nyan-cat.gif")
  //         left top
  //         no-repeat
  //       `,
  //         willOpen: () => {
  //             Swal.showLoading()
  //             this[func](record);
  //         },
  //         willClose: () => {
  //         }
  //     });
  // },

  async _drawDescriptor(image, result) {
    const img = await this.human.image(image);
    const canvas = img.canvas;

    let canvas2 = document.createElement("canvas");
    canvas2.width = canvas.width;
    canvas2.height = canvas.height;

    this.human.draw.all(canvas2, result);
    return canvas2.toDataURL();
  },

  _f32base64(descriptorArray1024) {
    // descriptor from float32 to base64 33% more data
    let f32base64 = btoa(
      String.fromCharCode(
        ...new Uint8Array(new Float32Array(descriptorArray1024).buffer),
      ),
    );
    return f32base64;
  },

  async _create_image(record) {
    let data = record.data;
    let vals = {
      descriptor: data.descriptor,
      image_detection: data.image_detection,
      image: data.image,
      name: data.name,
      sequence: data.sequence,
    };

    if (record.resModel == "res.users.image")
      vals.res_user_id = record.context.default_res_user_id;

    if (record.resModel == "hr.employee.image")
      vals.hr_employee_id = record.context.default_hr_employee_id;

    return this.rpc("/web/dataset/call_kw", {
      model: record.resModel,
      method: "create",
      kwargs: {},
      args: [vals],
    });
  },
});
