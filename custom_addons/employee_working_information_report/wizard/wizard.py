# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class EmployeeWorkingInformationReportWizard(models.TransientModel):
    _name = 'employee.working.information.report.wizard'
    _description = 'Employee Working Information Report Wizard'

    employee_ids = fields.Many2many('hr.employee', string="Employee")
    select_all_sub_employees = fields.Boolean(string="Select All Employee ?")

    @api.onchange('select_all_sub_employees')
    def _onchange_select_all_sub_employees(self):
        logged_in_employee = self.env.user.employee_id
        employee_ids_domain = [('id', '=', logged_in_employee.id)] if logged_in_employee else []
        sub_employees = self.env['hr.employee'].search([('parent_id', '=', logged_in_employee.id)])
        # if logged_in_employee.has_group('base.group_user'):  # Assuming only managers have access to certain groups
        time_off_officer = self.env['hr.leave.type'].search([('responsible_id', '=', self.env.user.id)])
        if self.select_all_sub_employees:
            if time_off_officer:
                self.employee_ids = self.env['hr.employee'].search([]).ids
            else:
                if sub_employees:
                    self.employee_ids = logged_in_employee.ids + sub_employees.ids
                else:
                    self.employee_ids = logged_in_employee.ids

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        logged_in_employee = self.env.user.employee_id
        employee_ids_domain = [('id', '=', logged_in_employee.id)] if logged_in_employee else []
        sub_employees = self.env['hr.employee'].search([('parent_id', '=', logged_in_employee.id)])
        # if logged_in_employee.has_group('base.group_user'):  # Assuming only managers have access to certain groups
        if sub_employees:
            sub_employees = self.env['hr.employee'].search([('parent_id', '=', logged_in_employee.id)])
            employee_ids_domain = [('id', 'in', [logged_in_employee.id] + sub_employees.ids)]
        else:
            employee_ids_domain = [('id', '=', logged_in_employee.id)]
        return {'domain': {'employee_ids': employee_ids_domain}}

    def process_report(self):
        data = {'form': self.read(['employee_ids'])[0]}
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['employee_ids'])[0])
        return self.env.ref("employee_working_information_report.action_report_employee_working_information_report").report_action(self, data=data)
