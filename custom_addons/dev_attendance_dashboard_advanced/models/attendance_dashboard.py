# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
import datetime
from odoo import http
from odoo.http import request
import math, calendar
import pytz
from odoo import models, fields, api, _
import datetime,calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import itertools
from operator import itemgetter
import operator
from datetime import date, timedelta
from datetime import datetime

class AttendanceDashboard(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def load_attendance_calendar_data(self, vals={}):
        user_tz = request.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        dept_val = vals.get('department_id')
        emp_val = vals.get('employee_id')
        month_val = vals.get('month_id') or datetime.today().month
        year_val = vals.get('year_id') or datetime.today().year
        employee_domain = []
        if dept_val and dept_val != 'all':
            dept_id = int(dept_val)
            employee_domain += [('department_id', '=', dept_id)]
        if emp_val and emp_val != 'all':
            employee_id = int(emp_val)
            employee_domain += [('id', '=', employee_id)]
        if month_val:
            month_val = int(month_val)
        if year_val:
            year_val = int(year_val)
        days = calendar.monthrange(year_val, month_val)[1]
        response = [[]]
        employee_ids = self.env['hr.employee'].search(employee_domain)
        days = calendar.monthrange(year_val, month_val)[1]
        for employee in employee_ids:
            emp_dict = {}
            att_dict = {}
            all_leaves = []
            all_present = []
            all_holidays = []
            leave = 0
            absent = 0
            present = 0
            weekoff = 0
            t_holiday = 0
            emp_dict['id'] = employee.id
            emp_img = ""

            if employee.avatar_128 and len(employee.avatar_128) > 1000:
                emp_img = employee.avatar_128
            else:
                emp_img = False
            emp_dict['img'] = emp_img
            emp_dict['name'] = employee.name
            emp_dict['job'] = employee.job_id.name

            for day in range(1, days + 1):
                check_in = datetime(year_val, month_val, day, 00, 00, 1)
                check_out = datetime(year_val, month_val, day, 23, 59, 59)
                employee_work_schedule = employee.resource_calendar_id.attendance_ids
                workingdays = list(set([int(schedule.dayofweek) for schedule in employee_work_schedule]))

                public_holiday_ids = employee.resource_calendar_id.global_leave_ids

                if check_in.weekday() not in workingdays:
                    att_dict[day] = {'status': 'W'}
                    weekoff += 1

                else:
                    leave_ids = self.env['hr.leave'].search(
                        [('employee_id', 'in', [employee.id]), ('request_date_from', '<=', check_in.date()),
                         ('request_date_to', '>=', check_out.date()), ('state', 'in', ['validate'])])

                    if leave_ids:
                        all_leaves.append(leave_ids.id)
                        att_dict[day] = {'status': 'l', 'ids': leave_ids.id}
                        leave += 1
                    else:
                        attendance_ids = self.env['hr.attendance'].search(
                            [('employee_id', 'in', [employee.id]), ('check_in', '>=', check_in),
                             ('check_out', '<=', check_out)], order='id asc')
                        if attendance_ids:
                            for att in attendance_ids.ids:
                                all_present.append(att)

                            total_hours = sum(att.worked_hours for att in attendance_ids)
                            td = timedelta(hours=total_hours)
                            hours, remainder = divmod(td.total_seconds(), 3600)
                            minutes = remainder // 60
                            att_dict[day] = {'status':'p', 'hours': '{:02}:{:02}'.format(int(hours), int(minutes)),'ids': attendance_ids.ids}
                            present += 1
                        else:
                            att_dict[day] = {'status': 'absent'}
                            absent += 1

                    for holiday in public_holiday_ids:
                        from_date = holiday.date_from.astimezone(local).date()
                        to_date = holiday.date_to.astimezone(local).date()

                        if from_date <= check_in.date() and to_date >= check_out.date():
                            if att_dict[day]['status'] == 'l':
                                leave-=1
                            att_dict[day] = {'status': 'holiday', 'ids': holiday.id}
                            all_holidays.append(holiday.id)
                            t_holiday += 1

            emp_dict['attendance'] = att_dict
            if all_leaves:
                emp_dict['all_leave'] = list(set(all_leaves))
            if all_present:
                emp_dict['all_present'] = all_present
            if all_holidays:
                emp_dict['all_holidays'] = all_holidays
            emp_dict['summary'] = {'w': weekoff, 'l': leave, 'p': present, 'a': absent - t_holiday, 'h': t_holiday}
            response[0].append(emp_dict)
        response.append({'days': days})
        return response

    @api.model
    def load_attendance_list_data(self, vals={}):
        dept_val = vals.get('department_id')
        emp_val=vals.get('employee_id')
        month_val = vals.get('month_id') or datetime.today().month
        year_val=vals.get('year_id') or datetime.today().year
        employee_domain =[]
        if dept_val and dept_val != 'all':
            dept_id = int(dept_val)
            employee_domain += [('employee_id.department_id', '=', dept_id)]
        if emp_val and emp_val != 'all':
            employee_id = int(emp_val)
            employee_domain += [('employee_id', '=', employee_id)]
        if month_val:
            month_val = int(month_val)
        if year_val:
            year_val = int(year_val)
        days = calendar.monthrange(year_val, month_val)[1]

        leave_details = self.env['hr.leave'].search_read(employee_domain+[('state', 'in', ['validate'])],['employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days_display', 'name'], order='request_date_from asc')
        new_leave_details = []
        for leave in leave_details:
            if leave['request_date_from'].month == month_val and leave['request_date_from'].year == year_val:
                new_leave_details.append(leave)
        return new_leave_details

    @api.model
    def load_users_and_partners(self):
        image = ""
        if self.env.user.image_1920 and len(self.env.user.image_1920) > 1000:
            image = self.env.user.image_1920
        else:
            image = False

        return {
            'department': self.env['hr.department'].sudo().search_read([],['name']),
            'employee': self.env['hr.employee'].sudo().search_read([], ['name']),
            'user_name': self.env.user.name,
            'user_img': image
        }



    
    
