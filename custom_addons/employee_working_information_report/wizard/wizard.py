# -*- coding: utf-8 -*-
from email.policy import default
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

def get_current_year():
    return str(datetime.utcnow().year)

def get_years():
    year_list = []
    for i in range(2010, 2050):
        year_list.append((str(i), str(i)))
    return year_list

month_choise=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                                    ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                                    ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')]

class EmployeeWorkingInformationReportWizard(models.TransientModel):
    _name = 'employee.working.information.report.wizard'
    _description = 'Employee Working Information Report Wizard'

    employee_ids = fields.Many2many('hr.employee', string="Employee",required=True)
    select_all_sub_employees = fields.Boolean(string="Select All Employee ?")
    start_year=fields.Selection(get_years(), string='Start Year',required=True ,default=get_current_year())
    start_month = fields.Selection(month_choise,string='Start Month',required=True,default='1')
    end_year = fields.Selection(get_years(), string='End Year',required=True,default=get_current_year())
    end_month = fields.Selection(month_choise,string='End Month',required=True,default=str(datetime.utcnow().month))

    @api.constrains('start_month', 'start_year','end_month','end_year')
    def _check_dates(self):
        for record in self:
            if record.end_year != record.start_year:
                if (record.end_year < record.start_year) :
                    raise ValidationError("End Year should be greater than Start Year.")
            else:
                if record.end_month< record.start_month:
                    raise ValidationError("End Month should be greater than Start Month.")


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
