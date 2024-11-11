# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta,time
import math
from odoo.tools.float_utils import float_round
from odoo.osv import expression
from pytz import timezone as TIMEZONE, utc
from dateutil.relativedelta import relativedelta


def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return time.max
    fractional, integral = math.modf(hours)
    return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)


class AcsPlanningTemplate(models.Model):
    _name = 'acs.planning.request'
    _inherit = ['mail.thread']
    _description = "Shift Planning"
    _order = 'id desc'

    def _planning_count(self):
        for record in self:
            emp_planning_count =self.env['acs.planning'].search_count([('planning_template_id','=',record.id)])
            record.planning_count=emp_planning_count

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', "Company")
    planning_line_ids = fields.One2many('acs.planning.line', 'planning_id', 'Planning Lines', readonly=False)
    note = fields.Text("Description", readonly=False)
    start_date = fields.Date("Start Date", required=True)
    end_date = fields.Date("End Date", required=True)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('waiting', 'Waiting for approval'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),],  string='State', default='draft',tracking=True)
    planning_count = fields.Integer('Planning #', compute='_planning_count')
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', required=True)
    approver_id = fields.Many2one('res.users','Approver')
    template_id = fields.Many2one('acs.planning.request.template', 'Template')
    planning_ids = fields.One2many('acs.planning', 'planning_template_id', 'Plannings', readonly=False)

    @api.onchange('template_id')
    def onchange_template_id(self):
        for rec in self:
            lines = []
            if rec.template_id:
                rec.planning_line_ids = False
                for line in rec.template_id.planning_line_ids:
                    lines.append((0, 0, {
                        'employee_id':line.employee_id.id,
                        'schedule_id': line.schedule_id.id,
                        'note':line.note,
                        'start_date':rec.start_date,
                        'end_date':rec.end_date
                    }))
                rec.planning_line_ids = lines

    def action_submit(self):
        self.state = "waiting"

    def acs_create_planning_line(self, line, start_date, end_date):
        self.env['acs.planning'].create({
            'employee_id':line.employee_id.id,
            'start_date': start_date,
            'end_date': end_date,
            'state':'approved',
            'schedule_id':line.schedule_id.id,
            'company_id':line.company_id.id,
            'planning_template_id':line.planning_id.id,
            'work_location_id': self.work_location_id.id,
        })

    def action_approve(self):
        for rec in self:
            for line in rec.planning_line_ids:
                date_range = [line.start_date+timedelta(days=x) for x in range((line.end_date-line.start_date).days)]
                for date in date_range:
                    week_day = date.weekday()
                    calendar_line = line.schedule_id

                    timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
                    # convert date and time into user timezone
                    self_tz = self.with_context(tz=timezone)

                    utcnow = TIMEZONE('utc').localize(datetime.utcnow()) # generic time
                    utc = utcnow.astimezone(TIMEZONE('utc')).replace(tzinfo=None)
                    user_time = utcnow.astimezone(TIMEZONE(timezone)).replace(tzinfo=None)
                    #Get the offset/difference of user timezone with the utc and deduct it from the dates to make it utc and then compare
                    #Case when the date end falls in the next day due to timezone difference, then in that case it will not be able to search the planning
                    offset = relativedelta(user_time, utc)
                    offset_hours  = offset.hours
                    offset_minutes  = offset.minutes
                    start_time = datetime.combine(date , float_to_time(calendar_line.hour_from))
                    end_time = start_time + timedelta(hours=calendar_line.duration)
                    if end_time.date() > start_time.date():
                        start_date = start_time - timedelta(hours=offset_hours, minutes=offset_minutes)
                        end_date = start_time.replace(hour=23, minute=59, second=59) - timedelta(hours=offset_hours, minutes=offset_minutes)
                        rec.acs_create_planning_line(line, start_date, end_date)
                        
                        start_date = datetime(start_time.year, start_time.month, start_time.day)+ timedelta(days=1) - timedelta(hours=offset_hours, minutes=offset_minutes)
                        end_date = end_time - timedelta(hours=offset_hours, minutes=offset_minutes)
                        rec.acs_create_planning_line(line, start_date, end_date)

                    else:
                        start_date = start_time - timedelta(hours=offset_hours, minutes=offset_minutes)
                        end_date = end_time - timedelta(hours=offset_hours, minutes=offset_minutes)
                        rec.acs_create_planning_line(line, start_date, end_date)

            rec.state = 'approved'
            rec.approver_id = self.env.user.id

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.planning_ids.state = 'cancel'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.planning_ids.unlink()

    def action_done(self):
        self.state = "done"

    def action_view_planning(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_planning.action_acs_planning")
        action['domain'] = [('planning_template_id','=',self.id)]
        return action

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_('Planning Request can be deleted only in Draft state.'))
        return super(AcsPlanningTemplate,self).unlink()

    def acs_check_employee_lines(self):        
        for record in self:
            employees = []
            for line in record.planning_line_ids:
                if line.employee_id.id in employees:
                    raise UserError(_('You cannot have more than one line with same employee .'))
                else:
                    employees.append(line.employee_id.id) 

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        record.acs_check_employee_lines()  
        return record

    def write(self,vals):
        res = super().write(vals)
        self.acs_check_employee_lines()  
        return res


class AcsPlanningLine(models.Model):
    _name = 'acs.planning.line'
    _description = "Shift Planning lines"
    _rec_name="employee_id"

    planning_id = fields.Many2one('acs.planning.request',  string='Planning Request', index=True, required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee',  string='Employee', index=True, required=True)
    start_date = fields.Date("Start Date", related='planning_id.start_date')
    end_date = fields.Date("End Date", related='planning_id.end_date')
    state = fields.Selection(string='Status', related='planning_id.state', store=True)
    company_id = fields.Many2one('res.company', "Company", related="planning_id.company_id")
    schedule_id = fields.Many2one('acs.time.table','Working Schedule', required=True)
    note = fields.Text('Note')

    @api.constrains('start_date', 'end_date', 'state', 'employee_id','schedule_id')
    def _check_date(self):
        domains = [[
            ('start_date', '<', planning.end_date),
            ('end_date', '>', planning.start_date),
            ('schedule_id', '=', planning.schedule_id.id),
            ('employee_id', '=', planning.employee_id.id),
            ('id', '!=', planning.id),
        ] for planning in self.filtered('employee_id')]
        domain = expression.AND([
            [('state', 'in', ['draft', 'waiting', 'approved', 'cancel', 'done'])],
            expression.OR(domains)
        ])
        if self.search_count(domain):
            raise ValidationError(_('You can not overlaps planning for same employee with same schedule for same date.'))


class AcsPlanning(models.Model):
    _name = 'acs.planning'
    _description = "Shift Planning"
    _rec_name="employee_id"

    @api.depends('start_date')
    def _get_date(self):
        for rec in self:
            rec.date = rec.start_date.date()

    employee_id = fields.Many2one('hr.employee',  string='Employee', index=True)
    start_date = fields.Datetime("Start Date", required=True)
    end_date = fields.Datetime("End Date", required=True)
    date = fields.Date(compute='_get_date',store=True)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('waiting', 'Waiting of Approval'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')],  string='Status', default='draft')
    company_id = fields.Many2one('res.company', "Company")
    planning_template_id = fields.Many2one('acs.planning.request', 'Planning Request')
    schedule_id = fields.Many2one('acs.time.table','Working Schedule')
    work_location_id = fields.Many2one('hr.work.location', 'Work Location')


class AcsPlanningRequestTemplate(models.Model):
    _name = 'acs.planning.request.template'
    _description = "Shift Planning Template"
    _order = 'id desc'

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', "Company")
    planning_line_ids = fields.One2many('acs.planning.request.line', 'planning_template_id', 'Planning Lines', readonly=False)
    note = fields.Text("Description", readonly=False)
    work_location_id = fields.Many2one('hr.work.location', 'Work Location',required=True)


class AcsPlanningTemplateLine(models.Model):
    _name = 'acs.planning.request.line'
    _description = "Shift Planning lines"
    _rec_name="employee_id"

    planning_template_id = fields.Many2one('acs.planning.request.template',  string='Request', index=True, required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee',  string='Employee', index=True, required=True)
    company_id = fields.Many2one('res.company', "Company", related="planning_template_id.company_id")
    schedule_id = fields.Many2one('acs.time.table','Working Schedule', required=True)
    note = fields.Text('Note')


class AcsTimetable(models.Model):
    _name = 'acs.time.table'
    _description = "Timetable"

    name = fields.Char("Name", required=True)
    hour_from = fields.Float("Start Hour", required=True)
    duration = fields.Float("Duration (Hour)", required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: