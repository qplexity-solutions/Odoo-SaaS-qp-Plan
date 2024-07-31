# -*- coding: utf-8 -*-
# from odoo import http


# class /mnt/extra-addons/hrPayrollExtension(http.Controller):
#     @http.route('//mnt/extra-addons/hr_payroll_extension//mnt/extra-addons/hr_payroll_extension', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//mnt/extra-addons/hr_payroll_extension//mnt/extra-addons/hr_payroll_extension/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('/mnt/extra-addons/hr_payroll_extension.listing', {
#             'root': '//mnt/extra-addons/hr_payroll_extension//mnt/extra-addons/hr_payroll_extension',
#             'objects': http.request.env['/mnt/extra-addons/hr_payroll_extension./mnt/extra-addons/hr_payroll_extension'].search([]),
#         })

#     @http.route('//mnt/extra-addons/hr_payroll_extension//mnt/extra-addons/hr_payroll_extension/objects/<model("/mnt/extra-addons/hr_payroll_extension./mnt/extra-addons/hr_payroll_extension"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/mnt/extra-addons/hr_payroll_extension.object', {
#             'object': obj
#         })
