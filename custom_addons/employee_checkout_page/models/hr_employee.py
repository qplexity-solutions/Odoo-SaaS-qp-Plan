# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError
import datetime


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def employee_checkout_page_info(self, user_id, employee_id):
        employee = self.env['hr.employee']
        if not user_id and employee_id:
            employee = employee.sudo().browse(employee_id)
            user_id = employee.sudo().user_id.id
        if user_id and not employee:
            employee = employee.sudo().search(
                [('user_id', '=', user_id)], limit=1)
        projects = self.env['project.project']
        if self.env.company.total_projects_to_display:
            projects = projects.sudo().search(
                [('user_id', '=', user_id)], order='create_date desc',
                limit=self.env.company.total_projects_to_display)

        if not employee:
            raise UserError(_('Employee not found!'))
        last_check_in = employee.last_check_in
        if last_check_in:
            last_check_in = last_check_in + datetime.timedelta(minutes=120)
        return {
            # 'last_check_in': employee.last_check_in + datetime.timedelta(minutes=120),
            'last_check_in': last_check_in,
            # 'last_check_in': employee.last_attendance_id.check_in,
            'assigned_projects': projects.mapped('name'),
            'total_holidays': employee.allocation_remaining_display,
            'total_overtime': employee.total_overtime,
        }
