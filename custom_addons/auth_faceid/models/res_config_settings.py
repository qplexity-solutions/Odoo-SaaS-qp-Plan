# Copyright 2019-2022 Artem Shurshilov
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


class ResConfigSettingsFaceid(models.TransientModel):
    _inherit = "res.config.settings"

    faceid_access = fields.Boolean(
        string="Enable face recognition access",
        help="Check in/out user only when face recognition do snapshot",
    )
    faceid_store = fields.Boolean(
        string="Store snapshots and descriptors employees?",
        help="Store snapshot and descriptor of employee when he check in/out in DB for visual control, takes up a lot of server space",
    )
    faceid_scale_recognition = fields.Integer(
        string="Scale of similafity face",
        help="0-100, 55 - standart value more 55 most stricter match",
        default=55,
    )
    faceid_scale_spoofing = fields.Integer(
        string="Scale of anti-spoofing",
        help="0-100, 100 - 100% person, 0 - disable, 70 - standart value",
        default=70,
    )
    faceid_photo_check = fields.Boolean(
        string="Enable face recognition check real person from photo/image",
        help="Check in/out user only if it live/real person not photo",
    )
    faceid_buffer_size_send = fields.Integer(
        string="Buffer size before sending",
        help="Count descriptors(photos) store for recognize on server",
        default=3,
    )
    faceid_hide_login = fields.Boolean(
        string="Hide login password",
        help="Hide password input and button",
        default=False,
    )
    faceid_fast_mode = fields.Boolean(
        string="Fast mode",
        help="Work very fast, dont show mask face or show very fast",
        default=True,
    )

    def set_values(self):
        res = super().set_values()
        config_parameters = self.env["ir.config_parameter"]
        config_parameters.set_param("faceid_access", self.faceid_access)
        config_parameters.set_param("faceid_store", self.faceid_store)
        config_parameters.set_param(
            "faceid_photo_check", self.faceid_photo_check
        )
        if (
            self.faceid_scale_recognition > 100
            or self.faceid_scale_spoofing > 100
            or self.faceid_scale_recognition < 0
            or self.faceid_scale_spoofing < 0
        ):
            raise ValidationError(
                "Error! Please check scale field allow range 0-100"
            )
        config_parameters.set_param(
            "faceid_scale_spoofing", self.faceid_scale_spoofing
        )
        config_parameters.set_param(
            "faceid_scale_recognition", self.faceid_scale_recognition
        )
        config_parameters.set_param(
            "faceid_buffer_size_send", self.faceid_buffer_size_send
        )
        config_parameters.set_param("faceid_hide_login", self.faceid_hide_login)
        config_parameters.set_param("faceid_fast_mode", self.faceid_fast_mode)
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            faceid_access=self.env["ir.config_parameter"].get_param(
                "faceid_access"
            )
        )
        res.update(
            faceid_store=self.env["ir.config_parameter"].get_param(
                "faceid_store"
            )
        )
        res.update(
            faceid_photo_check=self.env["ir.config_parameter"].get_param(
                "faceid_photo_check"
            )
        )
        res.update(
            faceid_hide_login=self.env["ir.config_parameter"].get_param(
                "faceid_hide_login"
            )
        )
        res.update(
            faceid_fast_mode=self.env["ir.config_parameter"].get_param(
                "faceid_fast_mode"
            )
        )

        faceid_scale_recognition = (
            self.env["ir.config_parameter"].get_param(
                "faceid_scale_recognition"
            )
            or 55
        )
        res.update(faceid_scale_recognition=faceid_scale_recognition)

        faceid_scale_spoofing = (
            self.env["ir.config_parameter"].get_param("faceid_scale_spoofing")
            or 70
        )
        res.update(faceid_scale_spoofing=faceid_scale_spoofing)

        faceid_buffer_size_send = (
            self.env["ir.config_parameter"].get_param("faceid_buffer_size_send")
            or 3
        )
        res.update(faceid_buffer_size_send=faceid_buffer_size_send)

        return res
