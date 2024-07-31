# models/attendance_request_wizard.py
from odoo import models, fields, api, _
import logging


class AttendanceRequestWizard(models.TransientModel):
    _name = 'attendance.request.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Attendance Request Wizard'

    attendance_id = fields.Many2one(comodel_name='hr.attendance', default=lambda self: self.env.context.get('active_id'))
    check_in = fields.Datetime('Check In')
    check_out = fields.Datetime('Check Out')
    reason = fields.Text('Reason')

    @api.onchange('attendance_id')
    def get_current_check_in_out(self):
        for record in self:
            if record.attendance_id:
                record.check_in = record.attendance_id.check_in
                record.check_out = record.attendance_id.check_out

    def action_request_change(self):
        self.ensure_one()
        attendance = self.attendance_id
        if attendance:
            vals = {
                'current_check_in': attendance.check_in,
                'current_check_out': attendance.check_out,
                'check_in': self.check_in,
                'check_out': self.check_out,
                'reason': self.reason,
                'attendance_id': attendance.id,
                'employee_id': attendance.employee_id.id,
                'state': 'submit',
            }
            request = self.env['attendance.request'].create(vals)
            admin = self.env['hr.employee'].sudo().search([('category_ids.name', '=', 'Zeitkontrolle')], limit=1).user_id.id
            if admin:
                activity_vals = {
                    'user_id': admin,
                    'res_id': request.id,
                    'summary': _(f"Employee requested attendance change to {self.check_in} and {self.check_out}"),
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_model_id': self.env.ref('attendance_request_approval.model_attendance_request').id,
                }
                self.env['mail.activity'].sudo().create(activity_vals)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Attendance Request'),
                'res_model': 'attendance.request',
                'view_mode': 'form',
                'res_id': request.id,
                'target': 'current',
            }
