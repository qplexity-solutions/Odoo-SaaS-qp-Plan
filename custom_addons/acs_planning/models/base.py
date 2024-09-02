# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_shift_employee = fields.Boolean('Is Shift Employee')


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    is_shift_employee = fields.Boolean('Is Shift Employee')
