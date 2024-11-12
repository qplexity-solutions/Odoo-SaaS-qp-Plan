from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.web.controllers.home import Home
from odoo.tools.translate import _
from odoo.http import request
from odoo import http

class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        request.env.registry.clear_all_caches()
        user = request.env.user.browse(request.session.uid)
        if not kw.get('debug') or kw.get('debug') != "0":
            cids = request.httprequest.cookies.get('cids') and request.httprequest.cookies.get('cids').split(',')[0] or request.env.company.id
            access_management = request.env['access.rights.management'].sudo().search([('active','=',True),('company_ids','in',int(cids)),('disable_debug_mode','=',True),('user_ids','in',user.id)],limit=1)
            if access_management.id:
                return request.redirect('/web?debug=0')
        return super(Home, self).web_client(s_action=s_action, **kw)
