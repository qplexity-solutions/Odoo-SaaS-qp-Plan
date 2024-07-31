# Copyright 2019 Artem Shurshilov
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettingsWebcam(models.TransientModel):
    _inherit = "res.config.settings"

    face_recognition_pro_backend = fields.Selection(
        [
            ("humangl", "humangl"),
            ("wasm", "wasm"),
            ("webgl", "webgl"),
            ("webgpu", "webgpu"),
            ("cpu", "cpu"),
        ],
        string="Backend",
        default="humangl",
    )
    face_recognition_pro_scale_recognition = fields.Integer(
        string="Scale of similafity face",
        help="0-100, 55 - standart value more 55 most stricter match",
        default=55,
    )
    face_recognition_pro_scale_spoofing = fields.Integer(
        string="Scale of anti-spoofing",
        help="0-100, 100 - 100% person, 0 - disable, 70 - standart value",
        default=70,
    )
    face_recognition_pro_photo_check = fields.Boolean(
        string="Enable face recognition check real person from photo/image",
        help="Check in/out user only if it live/real person not photo",
    )
    face_recognition_pro_access = fields.Boolean(
        string="Enable face recognition access",
        help="Check in/out user only when face recognition do snapshot",
    )
    face_recognition_pro_store = fields.Boolean(
        string="Store snapshots and descriptors employees?",
        help="Store snapshot and descriptor of employee when he check in/out in DB for visual control, takes up a lot of server space",
    )
    face_recognition_pro_kiosk_auto = fields.Boolean(
        string="Face recognition kiosk auto check in/out",
        help="Check in/out click auto when users face finded",
    )
    face_recognition_pro_timeout = fields.Integer(
        string="Face recognition timeout 5 secs after X fail, 0-disabled timeout",
        help="After X fail in a row, when recognizing, call a timeout of 5 seconds",
        default=0,
    )

    def set_values(self):
        res = super().set_values()
        cf = self.env["ir.config_parameter"]
        cf.set_param(
            "hr_attendance_face_recognition_pro_access",
            self.face_recognition_pro_access,
        )
        cf.set_param(
            "hr_attendance_face_recognition_pro_store",
            self.face_recognition_pro_store,
        )
        cf.set_param(
            "hr_attendance_face_recognition_pro_kiosk_auto",
            self.face_recognition_pro_kiosk_auto,
        )
        cf.set_param(
            "face_recognition_pro_photo_check",
            self.face_recognition_pro_photo_check,
        )
        cf.set_param(
            "face_recognition_pro_backend", self.face_recognition_pro_backend
        )
        if (
            self.face_recognition_pro_scale_recognition > 100
            or self.face_recognition_pro_scale_spoofing > 100
            or self.face_recognition_pro_scale_recognition < 0
            or self.face_recognition_pro_scale_spoofing < 0
        ):
            raise ValidationError(
                "Error! Please check scale field allow range 0-100"
            )
        cf.set_param(
            "face_recognition_pro_scale_spoofing",
            self.face_recognition_pro_scale_spoofing,
        )
        cf.set_param(
            "face_recognition_pro_timeout", self.face_recognition_pro_timeout
        )
        if self.face_recognition_pro_timeout < 0:
            raise ValidationError(
                "Error! Please check face timeout fail. Allow value should be 0 or more 10"
            )
        if (
            self.face_recognition_pro_timeout > 0
            and self.face_recognition_pro_timeout < 10
        ):
            raise ValidationError(
                "Error! Please check face timeout fail. Allow value should be 0 or more 10"
            )
        cf.set_param(
            "face_recognition_pro_scale_recognition",
            self.face_recognition_pro_scale_recognition,
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        cf = self.env["ir.config_parameter"]
        res.update(
            face_recognition_pro_access=cf.get_param(
                "hr_attendance_face_recognition_pro_access"
            )
        )
        res.update(
            face_recognition_pro_store=cf.get_param(
                "hr_attendance_face_recognition_pro_store"
            )
        )
        res.update(
            face_recognition_pro_kiosk_auto=cf.get_param(
                "hr_attendance_face_recognition_pro_kiosk_auto"
            )
        )
        res.update(
            face_recognition_pro_photo_check=cf.get_param(
                "face_recognition_pro_photo_check"
            )
        )

        res.update(
            face_recognition_pro_scale_recognition=cf.get_param(
                "face_recognition_pro_scale_recognition"
            )
            or 55
        )

        res.update(
            face_recognition_pro_scale_spoofing=cf.get_param(
                "face_recognition_pro_scale_spoofing"
            )
            or 70
        )

        res.update(
            face_recognition_pro_timeout=cf.get_param(
                "face_recognition_pro_timeout"
            )
            or 0
        )

        res.update(
            face_recognition_pro_backend=cf.get_param(
                "face_recognition_pro_backend"
            )
            or "humangl"
        )
        return res
