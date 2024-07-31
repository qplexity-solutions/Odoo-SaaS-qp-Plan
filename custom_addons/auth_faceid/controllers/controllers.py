# Copyright 2022 Artem Shurshilov
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

import base64
import math

import numpy as np

from odoo import http
from odoo.addons.web.controllers.main import _get_login_redirect_url
from odoo.http import request


class Faceid(http.Controller):
    @http.route("/auth_faceid/config", auth="none", type="json", cors="*")
    def index_config(self, **kw):
        res = {}

        faceid_access = (
            request.env["ir.config_parameter"].sudo().get_param("faceid_access")
        )
        faceid_store = (
            request.env["ir.config_parameter"].sudo().get_param("faceid_store")
        )
        faceid_photo_check = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_photo_check")
        )
        faceid_scale_recognition = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_scale_recognition")
        )
        faceid_scale_spoofing = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_scale_spoofing")
        )
        faceid_buffer_size_send = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_buffer_size_send")
        )
        faceid_hide_login = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_hide_login")
        )
        faceid_fast_mode = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_fast_mode")
        )

        res.update(
            {
                "faceid_scale_recognition": faceid_scale_recognition
                if faceid_scale_recognition
                else False,
                "faceid_scale_spoofing": faceid_scale_spoofing
                if faceid_scale_spoofing
                else False,
                "faceid_access": True if faceid_access else False,
                "faceid_store": True if faceid_store else False,
                "faceid_photo_check": True if faceid_photo_check else False,
                "faceid_buffer_size_send": faceid_buffer_size_send
                if faceid_buffer_size_send
                else False,
                "faceid_hide_login": True if faceid_hide_login else False,
                "faceid_fast_mode": True if faceid_fast_mode else False,
            }
        )
        return res

    @staticmethod
    def distance(descriptor1, descriptor2, options):
        #  general minkowski distance, euclidean distance is limited case where order is 2
        sum = 0
        for i in range(0, len(descriptor1)):
            # TODO work with order not 2 'true' if True else 'false'
            diff = (
                descriptor1[i] - descriptor2[i]
            )  #: (Math.abs(descriptor1[i] - descriptor2[i]));
            sum += diff * diff  #: (diff ** options.order);
        return (options["multiplier"] or 20) * sum

    #  invert distance to similarity, normalize to given range and clamp
    @staticmethod
    def normalizeDistance(dist, order, minn, maxx):
        if dist == 0:
            return 1  # short circuit for identical inputs
        # TODO work with order not 2 'true' if True else 'false'
        root = math.sqrt(dist)  #:  dist ** (1 / order); # take root of distance
        norm = (1 - (root / 100) - minn) / (maxx - minn)  # normalize to range
        clamp = max(min(norm, 1), 0)  # // clamp to 0..1
        return clamp

    @staticmethod
    def similarity(
        descriptor1,
        descriptor2,
        options={"order": 2, "multiplier": 25, "min": 0.2, "max": 0.8},
    ):
        dist = Faceid.distance(descriptor1, descriptor2, options)
        return Faceid.normalizeDistance(
            dist,
            options["order"] or 2,
            options["min"] or 0,
            options["max"] or 1,
        )

    @staticmethod
    def base64ToArray(descriptor):
        r = base64.decodebytes(str.encode(descriptor))
        q = np.frombuffer(r, dtype=np.float32)
        return q

    @http.route("/auth_faceid/email", auth="none", type="json", cors="*")
    def index(self, **kw):
        email = kw.get("email", False)
        if not email:
            return {"error": "Empty login"}

        user_id = (
            request.env["res.users"]
            .sudo()
            .search(
                ["|", ("email", "=", email), ("login", "=", email)], limit=1
            )
        )
        if not user_id:
            return {"error": "Wrong login"}

        descriptor_ids = kw.get("descriptors", False)
        if not descriptor_ids:
            return {"error": "Not found descriptors (faces)"}
        # origins
        # faces

        # 1 Take images from USERS where USER have related employee
        images_ids_users = (
            request.env["res.users.image"]
            .sudo()
            .search(
                [("res_user_id", "=", user_id.id), ("descriptor", "!=", False)]
            )
        )

        if not images_ids_users:
            return {"error": "Not found any faces on server"}

        faceid_scale_recognition = (
            int(
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("faceid_scale_recognition")
            )
            or 55
        )
        faceid_store = (
            request.env["ir.config_parameter"].sudo().get_param("faceid_store")
        )
        if faceid_store:
            origins = kw.get("origins", False)
            if not origins:
                return {
                    "error": "faceid_store is set to True, but no found origins"
                }
            faces = kw.get("faces", False)
            if not faces:
                return {
                    "error": "faceid_store is set to True, but no found faces"
                }

        for i in images_ids_users:
            d1 = Faceid.base64ToArray(i.descriptor)
            for index, j in enumerate(descriptor_ids):
                # TODO сделать большую точность как в js
                d2 = Faceid.base64ToArray(j)
                scale = Faceid.similarity(d1, d2)
                if 100 * scale > faceid_scale_recognition:
                    # login success
                    if faceid_store:
                        data = {"res_user_id": user_id.id, "descriptor": j}
                        data.update(
                            {"origin": origins[index], "face": faces[index]}
                        )
                        request.env["res.users.faceid.log"].sudo().create(data)
                    uid = request.session.authenticate(
                        request.session.db, email, {1}
                    )
                    request.params["login_success"] = True
                    redirect_url = _get_login_redirect_url(user_id.id, "/web")
                    return redirect_url

        return {"error": "Access denied"}
