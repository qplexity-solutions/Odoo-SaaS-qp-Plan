from odoo import models, fields, api
import logging
import math


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    time_in_decimal = fields.Char(compute='_compute_time_in_decimal', store=True, string="Time in Decimal")

    @api.depends('worked_hours', 'check_in', 'check_out')
    def _compute_time_in_decimal(self):
        for rec in self:
            hours, minutes = map(int, "{:.2f}".format(rec.worked_hours).split('.'))
            rec.time_in_decimal = "{:.2f}".format(hours + minutes / 60.0)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # task_properties = fields.Properties('Propertiess',
    #                                     definition='task_id.task_properties',
    #                                     copy=True)
    prop_name = fields.Char(string='Property Name', compute='_compute_prop_default')
    prop_value = fields.Char(string='Property Value', compute='_compute_prop_default')

    barcode = fields.Char(string='Badge_id', related='employee_id.barcode')

    def _compute_prop_default(self):
        for rec in self:
            # rec.prop1_default = rec.task_id.task_properties[0].get('value', False)
            prop_lst = [(x.get('string', False), x.get('value'))
                        for x in rec.task_id.task_properties
                        if x.get('value') is not False]
            if prop_lst:
                rec.prop_name = prop_lst[0][0]
                rec.prop_value = prop_lst[0][1]
            else:
                rec.prop_name = None
                rec.prop_value = None


class ProjectTask(models.Model):
    _inherit = 'project.task'
    prop_name = fields.Char(string='Property Name', compute='_compute_prop_default')
    prop_value = fields.Char(string='Property Value', compute='_compute_prop_default')

    # badge_id = fields.Char(string='Badge Id', compute='_compute_badge_id')

    def _compute_prop_default(self):
        for rec in self:
            # rec.prop1_default = rec.task_id.task_properties[0].get('value', False)
            prop_lst = [(x.get('string', False), x.get('value'))
                        for x in rec.task_properties
                        if x.get('value') is not False]
            if prop_lst:
                rec.prop_name = prop_lst[0][0]
                rec.prop_value = prop_lst[0][1]
            else:
                rec.prop_name = None
                rec.prop_value = None

    # def _compute_badge_id(self):
    #   emp_obj = self.env['hr.employee']
    #   for rec in self:
    #     badge_lst = []
    #     for user in rec.user_ids:
    #       badge_lst.append(emp_obj.search([('user_id', '=', user.id)]).barcode or ' ')
    #       logging.info(badge_lst)
    #     if badge_lst:
    #       badge_lst = '//'.join(badge_lst)
    #       rec.badge_id = badge_lst
    #     else:
    #       rec.badge_id = False
