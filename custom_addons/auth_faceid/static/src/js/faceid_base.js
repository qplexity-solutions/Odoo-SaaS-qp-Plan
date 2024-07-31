odoo.define("auth_faceid.base", function (require) {
  "use strict";

  require("web.dom_ready");
  var rpc = require("web.rpc");
  var Widget = require("web.Widget");
  var $camera = $("#camera-faceid");
  var FaceRecognitionAuthDialog = require("auth_faceid.dialog");

  var FaceidBase = Widget.extend({
    events: {
      "click #faceid-success": _.debounce(
        function () {
          this.update_attendance_with_recognition();
        },
        200,
        true,
      ),
    },

    // parse config setting from server
    parse_config_face_recognition: function (data) {
      this.face_recognition_pro_scale_recognition = Number(
        data.faceid_scale_recognition,
      );
      this.face_recognition_pro_scale_spoofing = Number(
        data.faceid_scale_spoofing,
      );
      this.face_recognition_enable = data.faceid_access;
      this.face_recognition_store = data.faceid_store;
      this.face_recognition_pro_photo_check = data.faceid_photo_check;
      this.face_recognition_buffer_size_send = Number(
        data.faceid_buffer_size_send,
      );
      this.face_recognition_fast_mode = data.faceid_fast_mode;
      // дикт для сохранения результатов распознования (весь буфер)
      this.resFaceId = {};
      this.resFaceId.descriptors = [];
      this.resFaceId.origins = [];
      this.resFaceId.faces = [];
      this.resFaceId.descriptorsArray = [];
      // число успешно распознанных лиц
      this.success_find_counter = 0;
      // число попыток
      this.try_find_counter = 0;
      // число наденных попыток обойти распознование
      this.spoof_find_counter = 0;

      if (!this.face_recognition_successfully)
        this.face_recognition_successfully = false;
    },

    init: function (parent) {
      console.log(this, "THIS");
      this.setElement(parent);
      this._super.apply(this, arguments);
    },

    load_models: async function () {
      let def = $.Deferred();
      const myConfig = {
        debug: false,
        async: true,
        backend: "humangl",
        modelBasePath: "/auth_faceid/static/src/js/models",
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
      this.human = await new Human.Human(myConfig);
      this.human.load().then(() => {
        def.resolve();
        console.log(this.human, "HUMAN load done");
      });
      return def;
    },

    load_config: function () {
      let def = $.Deferred();
      rpc
        .query({
          route: "/auth_faceid/config",
        })
        .then((data) => {
          def.resolve();
          this.data = data;
          this.parse_config_face_recognition(data);
          console.log(this, "CONFIG done");
        });
      return def;
    },

    start: function () {
      // parallel waiting
      Promise.all([this.load_models(), this.load_config()]).then((result) => {
        console.log("models and config success loaded");
        if (this.face_recognition_enable) {
          $("#faceid-loader").hide();
          $("#faceid-success").css("display", "flex");
        } else $("#faceid-loader").hide();
      });
      return $.when(this._super.apply(this, arguments));
    },

    update_attendance_with_recognition: function () {
      this.login = $('input[id="login"').val();
      if (!this.login) {
        Swal.fire({
          title: "Login empty",
          text: "Please set login first!",
          icon: "error",
          confirmButtonColor: "#3085d6",
          confirmButtonText: "Ok",
        });
        return;
      }

      new FaceRecognitionAuthDialog(this, {
        login: this.login,
      }).open();
    },
  });

  var FaceIdBase = new FaceidBase($camera);
  FaceIdBase.start();
  return FaceIdBase;
});
