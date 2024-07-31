from odoo import http
from odoo.addons.web.controllers.home import Home, ensure_db
from odoo.http import request


class Backend(Home):
    @http.route("/web/login", type="http", auth="none")
    def web_login(self, *args, **kw):
        ensure_db()
        res = {}

        # faceid_access = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_access')
        # faceid_store = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_store')
        # faceid_photo_check = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_photo_check')
        # faceid_scale_recognition = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_scale_recognition')
        # faceid_scale_spoofing = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_scale_spoofing')
        # faceid_buffer_size_send = request.env['ir.config_parameter'].sudo(
        # ).get_param('faceid_buffer_size_send')
        faceid_hide_login = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("faceid_hide_login")
        )

        res.update(
            {
                # 'faceid_scale_recognition': faceid_scale_recognition if faceid_scale_recognition else False,
                # 'faceid_scale_spoofing': faceid_scale_spoofing if faceid_scale_spoofing else False,
                # 'faceid_access': True if faceid_access else False,
                # 'faceid_store': True if faceid_store else False,
                # 'faceid_photo_check': True if faceid_photo_check else False,
                # 'faceid_buffer_size_send': faceid_buffer_size_send if faceid_buffer_size_send else False,
                "faceid_hide_login": faceid_hide_login
                or False
            }
        )
        response = super().web_login(*args, **kw)
        response.qcontext["faceid"] = res
        return response
