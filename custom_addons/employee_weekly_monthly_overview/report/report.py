# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools, _
from odoo.tools.float_utils import float_round
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import calendar


class EmployeeWeeklyMonthlyOverviewModel(models.AbstractModel):
    _name = 'report.employee_weekly_monthly_overview.information_report'
    _description = 'Employee Weekly & Monthly Overview Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        employee_ids = None

        if docs.employee_ids:
            employee_ids = docs.employee_ids
        year = docs.year
        month = docs.month
        overview_type = docs.overview_type

        records = self.env['hr.employee'].browse(employee_ids.ids)
        employees_list = []
        for record in records:
            # Get the current year
            # current_year = datetime.utcnow().year
            current_year = int(year)
            # Get the start and end dates of the current year
            start_of_year = datetime(current_year, 1, 1)
            end_of_year = datetime(current_year, 12, 30)
            # Define a list to store results
            hours_details = []
            if overview_type == 'monthly':
                # Loop through each month of the current year
                # for month in range(1, 13):
                month = int(month)
                # Get the first day of the month
                start_of_month = datetime(current_year, month, 1)
                # Get the last day of the month
                end_of_month = start_of_month + relativedelta(day=31)
                num_days_in_month = calendar.monthrange(current_year, month)[1]
                grand_total_working_hours = 0.0
                grand_total_worked_hours = 0.0
                grand_total_extra_hours = 0.0
                # Loop through each day of the selected month
                for day in range(1, num_days_in_month + 1):
                    # Get the date for the current day
                    current_date = datetime(current_year, month, day)
                    # Iterate over employees
                    for employee in record:
                        # Get the employee's work schedule (resource calendar)
                        resource_calendar = employee.resource_calendar_id
                        # Get the employee's timezone
                        tz = pytz.timezone(employee.tz or 'UTC')
                        # Convert start and end times to employee's timezone
                        start_naive = tz.localize(current_date).astimezone(pytz.utc).replace(tzinfo=None)
                        end_naive = start_naive + relativedelta(days=1) - relativedelta(seconds=1)  # End of the day
                        # Search for attendances within the current day
                        attendances = self.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            '&',
                            ('check_in', '<=', end_naive),
                            ('check_out', '>=', start_naive),
                        ])
                        # Calculate total working hours for the day
                        hours = 0.0
                        for attendance in attendances:
                            check_in = max(attendance.check_in, start_naive)
                            check_out = min(attendance.check_out, end_naive)
                            hours += (check_out - check_in).total_seconds() / 3600.0
                        # Round the total working hours to two decimal places
                        worked_hours = round(hours, 2)
                        grand_total_worked_hours += worked_hours
                        hr_leave = self.env['hr.leave'].sudo()._get_number_of_days(current_date, current_date, employee.id)
                        total_working_hours = round(hr_leave['hours'], 2) or 0.0
                        grand_total_working_hours += total_working_hours
                        # extra_hours = round(worked_hours - total_working_hours, 2)
                        extra_hour_records = self.env['hr.attendance.overtime'].sudo().search([('date', '=', current_date), ('employee_id', '=',
                                                                                                                             employee.id)]).duration
                        extra_hours = round(extra_hour_records, 2) or 0.0
                        grand_total_extra_hours += extra_hours
                        # Append results to the list
                        hours_details.append({
                            'name': current_date.strftime('%d-%b-%Y'),
                            'total_working_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(total_working_hours * 60, 60)),
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60)),
                            'extra_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(extra_hours * 60, 60)),
                        })
                hours_details.append({
                    'name': 'Total',
                    'total_working_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(grand_total_working_hours * 60, 60)),
                    'worked_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(grand_total_worked_hours * 60, 60)),
                    'extra_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(grand_total_extra_hours * 60, 60)),
                })

            if overview_type == 'weekly':
                start_of_week = start_of_year
                while start_of_week < end_of_year:
                    end_of_week = start_of_week + relativedelta(days=6)
                    # Iterate over employees
                    for employee in record:
                        # Get the employee's work schedule (resource calendar)
                        resource_calendar = employee.resource_calendar_id
                        # Get the employee's timezone
                        tz = pytz.timezone(employee.tz or 'UTC')
                        # Convert start and end times to employee's timezone
                        start_naive = tz.localize(start_of_week).astimezone(pytz.utc).replace(tzinfo=None)
                        end_naive = tz.localize(end_of_week).astimezone(pytz.utc).replace(tzinfo=None)
                        # Search for attendances within the current week
                        attendances = self.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            '&',
                            ('check_in', '<=', end_naive),
                            ('check_out', '>=', start_naive),
                        ])
                        # Calculate total working hours for the week
                        hours = 0.0
                        for attendance in attendances:
                            check_in = max(attendance.check_in, start_naive)
                            check_out = min(attendance.check_out, end_naive)
                            hours += (check_out - check_in).total_seconds() / 3600.0
                        # Round the total working hours to two decimal places
                        worked_hours = round(hours, 2)
                        hr_leave = self.env['hr.leave'].sudo()._get_number_of_days(start_of_week, end_of_week, employee.id)
                        total_working_hours = round(hr_leave['hours'], 2) or 0.0
                        extra_hours = round(worked_hours - total_working_hours, 2)
                        # Append results to the list
                        week_number = start_of_week.isocalendar()[1]
                        hours_details.append({
                            'name': f"Week {week_number} - {year}",
                            'total_working_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(total_working_hours * 60, 60)),
                            'worked_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(worked_hours * 60, 60)),
                            'extra_hours': '{0:02.0f}:{1:02.0f}'.format(*divmod(extra_hours * 60, 60)),
                        })
                    # Move to the start of the next week
                    start_of_week += relativedelta(weeks=1)
            employees_list.append({
                'employee': record,
                'hours_details': hours_details,
            })

        return {
            'docs': docs,
            'year': year,
            'month': datetime(int(year), int(month), 1).strftime('%B'),
            'overview_type': overview_type,
            'records': employees_list,  # complete records
        }
