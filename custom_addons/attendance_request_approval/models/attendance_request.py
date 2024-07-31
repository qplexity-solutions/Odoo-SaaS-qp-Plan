# models/__init__.py
from . import attendance_request

# models/attendance_request.py
from odoo import models, fields, api, _
import logging


class AttendanceRequest(models.Model):
    _name = 'attendance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Attendance Request'

    name = fields.Char(string='Request Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    current_check_in = fields.Datetime('Current Check In', track_visibility='always')
    current_check_out = fields.Datetime('Current Check Out', track_visibility='always')
    check_in = fields.Datetime('Requested Check In', track_visibility='always')
    check_out = fields.Datetime('Requested Check Out', track_visibility='always')
    reason = fields.Text(string='Reason', track_visibility='always')
    attendance_id = fields.Many2one('hr.attendance', string='Attendance Record', required=True, track_visibility='always')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env.user.employee_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approved_team_lead', 'Approved by Team Lead'),
        ('approved_time_officer', 'Approved by Time Officer'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def action_approve_team_lead(self):
        self.write({'state': 'approved_team_lead'})

    def action_approve_time_officer(self):
        for request in self:
            request.state = 'approved_time_officer'
            if request.attendance_id:
                request.attendance_id.write({
                    'check_in': request.check_in,
                    'check_out': request.check_out,
                })

    def action_reject(self):
        for request in self:
            request.state = 'rejected'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('attendance.request') or _('New')
        record = super(AttendanceRequest, self).create(vals)
        # Activity creation logic for admin
        admin = self.env['hr.employee'].sudo().search([('category_ids.name', '=', 'Zeitkontrolle')], limit=1).user_id
        if admin:
            activity_vals = {
                'res_model_id': self.env.ref('attendance_request_approval.model_attendance_request').id,
                'res_id': record.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _(f"Approval required for attendance request by {record.employee_id.name}"),
                'user_id': admin.id,
            }
            self.env['mail.activity'].sudo().create(activity_vals)
        return record

    def unlink(self):
        for request in self:
            if request.state in ('approved', 'rejected'):
                raise models.ValidationError(_('You cannot delete a processed attendance request.'))
        return super(AttendanceRequest, self).unlink()
