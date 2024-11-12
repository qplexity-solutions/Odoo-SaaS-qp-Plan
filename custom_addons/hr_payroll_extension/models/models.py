# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class HRLeaveInherite(models.Model):
    _inherit = 'hr.leave'
    testing = fields.Char(string="Testing")

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._check_overtime_deductible(res)
        return res

    def write(self, values):
        if 'active' in values and not self.env.context.get('from_cancel_wizard'):
            raise UserError(_("You can't manually archive/unarchive a time off."))

        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.is_superuser()
        if not is_officer and values.keys() - {'attachment_ids', 'supported_attachment_ids', 'message_main_attachment_id'}:
            if any(hol.date_from.date() < fields.Date.today() and hol.employee_id.leave_manager_id != self.env.user for hol in self):
                raise UserError(_('You must have manager rights to modify/validate a time off that already begun'))

        # Unlink existing resource.calendar.leaves for validated time off
        if 'state' in values and values['state'] != 'validate':
            validated_leaves = self.filtered(lambda l: l.state == 'validate')
            validated_leaves._remove_resource_leave()

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']

        result = super(HRLeaveInherite, self).write(values)

        if any(field in values for field in ['request_date_from', 'date_from', 'request_date_from', 'date_to', 'holiday_status_id', 'employee_id']):
            self._check_validity()
        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)

        return result

    def action_draft(self):
        overtime_leaves = self.filtered('overtime_deductible')

        # Correction: Loop through each leave in overtime_leaves
        for leave in overtime_leaves:
            employee = leave.employee_id.sudo()
            duration = leave.number_of_hours_display
            if duration > 100:
                if employee.user_id == self.env.user:
                    raise ValidationError(_('You do not have enough extra hours to request this leave'))
                raise ValidationError(_('The employee does not have enough extra hours to request this leave.'))

        res = super().action_draft()

        for leave in overtime_leaves:
            overtime_leaves.overtime_id.sudo().unlink()
            overtime = self.env['hr.attendance.overtime'].sudo().create({
                'employee_id': leave.employee_id.id,
                'date': leave.date_from,
                'adjustment': True,
                'duration': -1 * leave.number_of_hours_display
            })
            leave.sudo().overtime_id = overtime.id

        return res

    def _check_overtime_deductible(self, leaves):

        # If the type of leave is overtime deductible, we have to check that the employee has enough extra hours
        for leave in leaves:
            if not leave.overtime_deductible:
                continue
            employee = leave.employee_id.sudo()
            duration = leave.number_of_hours_display
            print("DDDDDDDD : ", duration)
            if duration > 100:
                if employee.user_id == self.env.user:
                    raise ValidationError(_('You do not have enough extra hours to request this leave'))
                raise ValidationError(_('The employee does not have enough extra hours to request this leave.'))

            # # Additional validation for duration less than 80 hours
            # if duration < 80:
            #     raise ValidationError(_('Leave duration must be at least 80 hours for overtime deductible leave.'))

            if not leave.overtime_id:
                leave.sudo().overtime_id = self.env['hr.attendance.overtime'].sudo().create({
                    'employee_id': employee.id,
                    'date': leave.date_from,
                    'adjustment': True,
                    'duration': -1 * duration,
                })

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            mapped_days = self.holiday_status_id.get_employees_days((holiday.employee_id | holiday.sudo().employee_ids).ids, holiday.date_from.date())
            if holiday.holiday_type != 'employee' \
                    or not holiday.employee_id and not holiday.sudo().employee_ids \
                    or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            if holiday.employee_id:
                leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
                if holiday.holiday_status_id.name == 'Extra Hours':
                    duration = holiday.number_of_hours_display
                    if duration > 80:
                        raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                                'Please also check the time off waiting for validation.'))
                else:
                    if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 \
                            or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                        raise ValidationError(_('Hehe. The number of remaining time off is not sufficient for this time off type.\n'
                                                'Please also check the time off waiting for validation.'))
            else:
                unallocated_employees = []
                for employee in holiday.sudo().employee_ids:
                    leave_days = mapped_days[employee.id][holiday.holiday_status_id.id]
                    if float_compare(leave_days['remaining_leaves'], self.number_of_days, precision_digits=2) == -1 \
                            or float_compare(leave_days['virtual_remaining_leaves'], self.number_of_days, precision_digits=2) == -1:
                        unallocated_employees.append(employee.name)
                if unallocated_employees:
                    raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                                            'Please also check the time off waiting for validation.')
                                          + _('\nThe employees that lack allocation days are:\n%s',
                                              (', '.join(unallocated_employees))))
