odoo.define("auth_faceid.dialog", function (require) {
  "use strict";

  var config = require("web.config");
  var Dialog = require("web.Dialog");
  var core = require("web.core");
  var rpc = require("web.rpc");
  var _t = core._t;

  var FaceRecognitionAuthDialog = Dialog.extend({
    xmlDependencies: [
      "/auth_faceid/static/src/xml/FaceRecognitionAuthDialog.xml",
      "/web/static/src/legacy/xml/dialog.xml",
    ],

    template: "FaceRecognitionAuthDialog",

    init: function (parent, options) {
      options = options || {};
      options.fullscreen = config.device.isMobile;
      options.fullscreen = true;
      options.dialogClass = options.dialogClass || "" + " o_act_window";
      options.size = "large";
      options.title = _t("Face recognition auth process");
      this.parent = parent;
      this._super(parent, options);
    },

    handleStream: async function (stream) {
      let def = $.Deferred();
      const video = this.$el.find("video")[0];

      // отображаем видео в диалоге
      video.srcObject = stream;
      video.play();
      video.addEventListener(
        "loadedmetadata",
        (e) => {
          this.streamStarted = true;
          def.resolve();
        },
        false,
      );

      return def;
    },

    start_video: async function () {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { min: 640, ideal: 1280 },
            height: { min: 480, ideal: 720 },
          },
        });
        await this.handleStream(videoStream);
      } catch (e) {
        console.error("*** getUserMedia", e);
      } finally {
      }
    },

    start: function () {
      return this._super.apply(this, arguments).then(async () => {
        // запрашиваем разрешение на доступ к поточному видео камеры
        // и запускаем видео с камеры
        await this.start_video();

        // подготавливаем канвас для отрисовки видео
        let res = await this.drawVideoPrepare("video", "#faceid_canvas");
        if (res)
          // отрисовываем видео на канвас и распознаем
          this.drawVideo(res[0], res[1]);
      });
    },

    server_verify: function (paramsData) {
      let def = $.Deferred();
      rpc
        .query({
          route: "/auth_faceid/email",
          params: paramsData,
        })
        .then((data) => {
          def.resolve(data);
        });
      return def;
    },

    check_in_out: function () {
      // делаем логин сотрудника, через дебаунси, чтобы предотвратить двойной вызов
      var debounced = _.debounce(
        async () => {
          // this.parent.face_recognition_successfully = true;
          // SERVER VERIFY
          let response = await this.server_verify(
            _.extend({}, this.parent.resFaceId, { email: this.parent.login }),
          );
          Swal.close();
          if (response.error)
            Swal.fire({
              title: "Server verify error",
              text: response.error,
              icon: "error",
              confirmButtonColor: "#3085d6",
              confirmButtonText: "Ok",
            });
          else {
            Swal.fire({
              title: "Verify success",
              text: "Welcome!",
              icon: "success",
              confirmButtonColor: "#3085d6",
              confirmButtonText: "Ok",
            });
            window.location = response;
          }
        },
        600,
        true,
      );
      debounced();
    },

    antiSpoofingCheck: async function (image) {
      await tf.ready();
      // load model
      const model = await tf.loadGraphModel(
        "/auth_faceid/static/src/js/models/anti-spoofing.json",
      );
      const resized = tf.image.resizeBilinear(image, [128, 128]);
      const expanded = tf.expandDims(resized, 0);
      const res = model.execute(expanded, ["activation_4"]);
      return res.dataSync()[0];
    },

    _f32base64: function (descriptorArray1024) {
      // descriptor from float32 to base64 33% more data
      let f32base64 = btoa(
        String.fromCharCode(
          ...new Uint8Array(new Float32Array(descriptorArray1024).buffer),
        ),
      );
      return f32base64;
    },

    face_detection: async function (canvas) {
      // если набрали лиц с размером в буфер
      if (
        this.parent.success_find_counter >=
        this.parent.face_recognition_buffer_size_send
      ) {
        Swal.fire({
          title: "Verify on server",
          html: "I will close in automaticaly",
          timerProgressBar: true,
          allowOutsideClick: false,
          showCloseButton: false,
          showConfirmButton: false,
          icon: "info",
          willOpen: () => {
            Swal.showLoading();
            this.check_in_out();
          },
          willClose: () => {
            this.destroy();
          },
        });
        this.destroy();
        return;
      }

      // если долго не находили лицо закрываем
      if (this.parent.try_find_counter > 50) {
        Swal.fire({
          title: "Long time not find faces",
          text: "Please show your face",
          icon: "warning",
          confirmButtonColor: "#3085d6",
          confirmButtonText: "Ok",
        });
        this.destroy();
        return;
      }

      if (this.parent.spoof_find_counter > 2) {
        Swal.fire({
          title: "Spoofing detect!",
          text: "Please dont try use photo!",
          icon: "error",
          confirmButtonColor: "#3085d6",
          confirmButtonText: "Ok",
        });
        this.destroy();
        return;
      }

      const result = await this.parent.human.detect(canvas);
      let res = "face not found";
      if (result.face.length) {
        // check spoofing
        if (this.parent.face_recognition_pro_photo_check) {
          // let check = await this.antiSpoofingCheck(result.face[0].tensor)
          let check = result.face[0].real;
          console.log(this.parent.face_recognition_pro_scale_spoofing);
          console.log(
            "check: " + check,
            Number(this.parent.face_recognition_pro_scale_spoofing) / 100,
          );
          if (
            check <
            Number(this.parent.face_recognition_pro_scale_spoofing) / 100
          )
            res = "spoof";
        }

        // store clear face
        if (this.parent.face_recognition_store) {
          const canvas = this.$el.find("#faceid_canvas")[0];
          this.parent.resFaceId.origins.push(canvas.toDataURL().split(",")[1]);
        }

        // draw human metadata and face
        await this.parent.human.draw.all(canvas, result);

        // store founded face
        const found = result.face[0].embedding;
        this.parent.resFaceId.descriptorsArray.push(found);
        this.parent.resFaceId.descriptors.push(this._f32base64(found));

        // store human face data
        if (this.parent.face_recognition_store) {
          let imageDescriptorBase64 = await this._getImageFromHuman(
            canvas,
            result,
          );
          this.parent.resFaceId.faces.push(imageDescriptorBase64.split(",")[1]);
        }

        if (res != "spoof") res = "face added";
      }

      // если не нашли лицо продолжаем распознование
      if (res == "face not found") this.parent.try_find_counter += 1;

      // если нашли лицо, то добавляем
      if (res == "face added") this.parent.success_find_counter += 1;

      // если нашли спуфинг атаку
      if (res == "spoof") this.parent.spoof_find_counter += 1;

      if (this.parent.face_recognition_fast_mode) await this.sleep(10);
      else await this.sleep(300);
      this.face_detection(canvas);
    },

    _getImageFromHuman: async function (size, result) {
      // create new canvas
      let can = document.createElement("canvas");
      can.width = size.width;
      can.height = size.height;

      // draw human output and return as image base64
      this.parent.human.draw.all(can, result);
      return can.toDataURL();
    },

    sleep: function (ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },

    drawVideoPrepare: function (sourceSelector, canvasSelector) {
      let def = $.Deferred();
      let video = null;

      if (this.streamStarted) video = this.$el.find(sourceSelector)[0];

      // не нашли видео элемента или поток не запущен
      // или распознование завершено
      if (!video || !this.streamStarted) def.resolve(null);

      var canvas = this.$el.find(canvasSelector)[0];
      if (!canvas) def.resolve(null);

      def.resolve([canvas, video]);
      return def;
    },

    drawVideo: async function (canvas, video) {
      // отрисовка прекращается при закрытии диалога
      if (!this.streamStarted) return;

      // если изображение с камеры слишком большое
      // уменьшаем его до размера диалогового окна
      if (video.videoWidth > this.$el.width()) {
        canvas.width = this.$el.width();
        canvas.height =
          (this.$el.width() * video.videoHeight) / video.videoWidth;
      } else {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }

      // отрисовываем видео
      canvas
        .getContext("2d")
        .drawImage(video, 0, 0, canvas.width, canvas.height);

      if (!this.faceidStarted) this.face_detection(canvas);
      this.faceidStarted = true;

      // рисуем видео с камеры 100fps
      if (this.parent.face_recognition_fast_mode) await this.sleep(10);
      else await this.sleep(300);
      this.drawVideo(canvas, video);
    },

    destroy: function () {
      // останавливае распознование, если отключаем камеру
      this.streamStarted = false;
      this.parent.resFaceId = {};
      this.parent.resFaceId.descriptors = [];
      this.parent.resFaceId.origins = [];
      this.parent.resFaceId.faces = [];
      this.parent.resFaceId.descriptorsArray = [];
      this.parent.success_find_counter = 0;
      this.parent.try_find_counter = 0;
      this.parent.spoof_find_counter = 0;
      this.$el
        .find("video")[0]
        .srcObject.getTracks()
        .forEach((track) => {
          track.stop();
        });
      this._super.apply(this, arguments);
    },
  });

  return FaceRecognitionAuthDialog;
});
