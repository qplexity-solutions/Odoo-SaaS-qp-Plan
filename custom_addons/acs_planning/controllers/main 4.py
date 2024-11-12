# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError


class PlanningPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        AcsPlanning = request.env['acs.planning']
        if 'planning_count' in counters:
            values['planning_count'] = AcsPlanning.search_count([('state','in',['approved','done'])]) \
                if AcsPlanning.check_access_rights('read', raise_exception=False) else 0
        return values
    
    @http.route(['/my/plannings', '/my/plannings/page/<int:page>'], type='http', auth="user", website=True, sitemap=False)
    def my_plannings(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
        count = request.env['acs.planning'].search_count([('state','in',['approved','done'])])
 
        pager = portal_pager(
            url="/my/plannings",
            url_args={},
            total=count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        Plannings = request.env['acs.planning'].search([('state','in',['approved','done'])],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'plannings': Plannings,
            'page_name': 'Plannings',
            'default_url': '/my/plannings',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_planning.my_plannings", values)

    @http.route(['/my/plannings/<int:planning_id>'], type='http', auth="user", website=True, sitemap=False)
    def my_acs_plannings_planning(self, planning_id=None, access_token=None, **kw):
        try:
            record_sudo = self._document_check_access('acs.planning', planning_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_planning.my_acs_plannings_planning", {'planning': record_sudo})