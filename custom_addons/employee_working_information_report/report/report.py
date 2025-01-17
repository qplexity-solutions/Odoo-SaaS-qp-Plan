# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools, _
from odoo.tools.float_utils import float_round
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import calendar
from collections import defaultdict
from odoo.addons.resource.models.resource import Intervals


class EmployeeWorkingInformationReportModel(models.AbstractModel):
    _name = 'report.employee_working_information_report.information_report'
    _description = 'Employee Working Information Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        employee_ids = None
        start_year =None
        end_year =None
        start_month =None
        end_month =None
        if docs.employee_ids:
            employee_ids = docs.employee_ids
            start_year =int(docs.start_year)
            end_year =int(docs.end_year)+1
            end_month = int(docs.end_month)
            start_month =int(docs.start_month)

        records = self.env['hr.employee'].browse(employee_ids.ids)
        employees_list = []
        for record in records:
            # Get the current year
            current_year = datetime.utcnow().year
            # Get the start and end dates of the current year
            # start_of_year = datetime(current_year, 1, 1)
            # end_of_year = datetime(current_year, 12, 31)
            # Previous Year Calculations
            previous_year = current_year - 1
            # Define the extra_hours_balance variable to keep track of the balance
            extra_hours_balance = 0
            # Get entitlement for the previous year
            # Calculate the start and end dates of the previous year
            previous_year_start = datetime(previous_year, 1, 1)
            previous_year_end = datetime(previous_year, 12, 31)
            extra_hours_records = self.env['hr.attendance.overtime'].sudo().search([('employee_id', '=', record.id), ('date', '>=', previous_year_start),
                                                                                    ('date', '<=', previous_year_end)])
            if extra_hours_records:
                for hour in extra_hours_records:
                    extra_hours_balance += hour.duration
            previous_year_allocation_data = self.env['hr.leave.allocation'].sudo().search([
                ('employee_id', '=', record.id),
                ('state', '=', 'validate'),
                ('holiday_status_id.name', '=', 'Ferien')
            ])
            previous_year_entitlement = float_round(sum(previous_year_allocation_data.filtered(lambda x: x.date_from.year ==
                                                                                                         previous_year).mapped(
                'number_of_days_display')), precision_digits=2) if previous_year_allocation_data else 0.0
            # Get taken holidays for the current year
            previous_year_taken_holidays = self.env['hr.leave'].search([
                ('employee_id', '=', record.id),
                ('request_date_from', '>=', datetime(previous_year, 1, 1)),
                ('request_date_to', '<=', datetime(previous_year, 12, 31)),
                ('state', '=', 'validate'),  # Filter by the state of the leave request (approved)
                ('holiday_status_id.name', '=', 'Ferien')
            ])
            previous_year_total_taken_holidays = sum(leave.number_of_days for leave in previous_year_taken_holidays) or 0.0
            previous_year_remaining_holidays = float_round(previous_year_entitlement - previous_year_total_taken_holidays, precision_digits=2)
            previous_year_remaining_holidays = 0.0 if previous_year_remaining_holidays < 0 else previous_year_remaining_holidays
            # Previous Year Calculations Ends Here
            # Define a list to store results
            yearly_hours_details = []
            employee_data_datails =[]
            previous_years_extra_hours = extra_hours_balance

            def get_last_day_of_month(year, month):
                # Calculate the last day of the given month
                if month == 12:
                    return datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    return datetime(year, month + 1, 1, 23, 59, 0) - timedelta(days=1)

            for i in range(start_year,end_year):
                start_month_value = 1
                end_month_value = 12

                if i == start_year:
                    start_month_value=start_month
                if i == end_year-1:
                    end_month_value=end_month

                start_of_year = datetime(i, 1, 1)
                end_of_year = datetime(i, 12, 31)

                for month in range(start_month_value, end_month_value+1):
                    # Get the first and last day of the month
                    start_of_month = datetime(i, month, 1)
                    end_of_month = get_last_day_of_month(i, month)
                    for employee in record:
                        # Get the employee's timezone
                        tz = pytz.timezone(employee.tz or 'UTC')

                        # Convert start and end times to employee's timezone
                        # start_utc = tz.localize(start_of_month).astimezone(pytz.utc).replace(tzinfo=None)
                        # end_utc = tz.localize(end_of_month).astimezone(pytz.utc).replace(tzinfo=None)

                        # Search for attendances within the current month
                        attendances = self.env['hr.attendance'].sudo().search([
                            ('employee_id', '=', employee.id),
                            ('check_in', '>=', start_of_month),
                            ('check_out', '<=', end_of_month),
                        ])
                        print(len(attendances))
                        # Calculate total working hours for the month
                        total_hours = 0.0
                        for attendance in attendances:
                            if attendance.check_in and attendance.check_out:
                                # Ensure the attendance is within the month range
                                # check_in = max(attendance.check_in, start_of_month)
                                # check_out = min(attendance.check_out, end_of_month)
                                # total_hours += (check_out - check_in).total_seconds() / 3600.0
                                total_hours += attendance.worked_hours

                        # Calculate holidays and add 8.2 hours for each holiday
                        holidays = self.env['hr.leave'].sudo().search([
                            ('employee_id', '=', employee.id),
                            ('request_date_from', '>=', start_of_month),
                            ('request_date_to', '<=', end_of_month),
                            ('state', '=', 'validate'),
                            ('holiday_status_id.name', 'not in', ['Unpaid', 'Compensatory Days', 'Extra Hours']),
                        ])

                        for holiday in holidays:
                            days_on_holiday = (holiday.request_date_to - holiday.request_date_from).days + 1
                            total_hours += days_on_holiday * 8.2
                        # Round the total working hours to two decimal places
                        worked_hours = float_round(total_hours, precision_digits=2)
                        print(f"Employee ID: {employee.id}, Month: {month}, Worked Hours: {worked_hours}")
                        hr_leave = self.env['hr.leave'].sudo()._get_number_of_days(start_of_month, end_of_month, employee.id)
                        total_working_hours = float_round(hr_leave['hours'], precision_digits=2) or 0.0
                        extra_hours = float_round(worked_hours - total_working_hours, precision_digits=2)
                        extra_hours_balance += extra_hours
                        month_name = calendar.month_name[month]
                        # Append results to the list
                        yearly_hours_details.append({
                            'month': f"{month_name} ( {i} )",
                            'total_working_hours': round(total_working_hours, 2),
                            'twh_style': "color: black;" if abs(total_working_hours) >= 60 else "color: black;",
                            'worked_hours': round(worked_hours, 2),
                            'wh_style': "color: black;" if abs(worked_hours) >= 60 else "color: black;",
                            'extra_hours': round(extra_hours, 2),
                            'eh_style': "color: black;" if abs(extra_hours) >= 60 else "color: black;",
                            'extra_hours_balance': round(extra_hours_balance, 2),
                            'ehb_style': "color: black;" if abs(extra_hours_balance) >= 60 else "color: black;",
                        })
            # Get entitlement for the current year
                current_year_allocation_data = self.env['hr.leave.allocation'].sudo().search([
                    ('employee_id', '=', record.id),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.name', '=', 'Ferien')
                ])
                current_year_total_entitlement = float_round(sum(current_year_allocation_data.filtered(lambda x: x.date_from.year ==
                                                                                                                 current_year).mapped(
                    'number_of_days_display')),
                                                             precision_digits=2) if current_year_allocation_data else 0.0
                total_entitlement = float_round(current_year_total_entitlement + previous_year_remaining_holidays, precision_digits=2)
                # Get taken holidays for the current year
                current_year_taken_holidays = self.env['hr.leave'].search([
                    ('employee_id', '=', record.id),
                    ('request_date_from', '>=', datetime(current_year, 1, 1)),
                    ('request_date_to', '<=', datetime(current_year, 12, 31)),
                    ('state', '=', 'validate'),  # Filter by the state of the leave request (approved)
                    ('holiday_status_id.name', '=', 'Ferien')
                ])
                current_year_total_taken_holidays = sum(leave.number_of_days for leave in current_year_taken_holidays) if current_year_taken_holidays else 0.0
                total_taken_holidays = float_round(current_year_total_taken_holidays, precision_digits=2)
                # Calculate remaining holidays
                remaining_holidays = float_round(total_entitlement - total_taken_holidays, precision_digits=2)

                # Search for leave requests for the current year and the specified employee
                time_offs = self.env['hr.leave'].search([
                    ('employee_id', '=', record.id),
                    ('request_date_from', '>=', start_of_year),
                    ('request_date_to', '<=', end_of_year),
                    ('holiday_status_id.name', '=', 'Extra Hours'),
                    ('state', '=', 'validate')  # Optionally, filter by the state of the leave request
                ])
                # Define a list to store time-offs details
                time_offs_details = []
                # Iterate over the leave requests and append details to the list
                for leave in time_offs:
                    # Calculate the duration in hours
                    duration_hours = (leave.request_date_to - leave.request_date_from).total_seconds() / 3600
                    # Append details to the list
                    time_offs_details.append({
                        'from_date': leave.request_date_from,
                        'to_date': leave.request_date_to,
                        'hours': duration_hours,
                        'description': leave.name
                    })

                # Search for approved leave requests (holidays) for the current year and the specified employee
                approved_holidays = self.env['hr.leave'].search([
                    ('employee_id', '=', record.id),
                    ('request_date_from', '>=', start_of_year),
                    ('request_date_to', '<=', end_of_year),
                    ('state', '=', 'validate'),  # Filter by the state of the leave request (approved)
                    ('holiday_status_id.name', '=', 'Ferien')
                ])

                # Define a list to store approvFed holidays details
                approved_holidays_details = []

                # Iterate over the approved leave requests and append details to the list
                for leave in approved_holidays:
                    # Calculate the number of days for the leave request
                    # duration_days = (leave.request_date_to - leave.request_date_from).days + 1
                    duration_days = leave.number_of_days_display

                    # Append details to the list
                    approved_holidays_details.append({
                        'from_date': leave.request_date_from,
                        'to_date': leave.request_date_to,
                        'days': duration_days
                    })

                # Search for approved leave requests (sick leaves) for the current year and the specified employee
                approved_sick_leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', record.id),
                    ('request_date_from', '>=', start_of_year),
                    ('request_date_to', '<=', end_of_year),
                    ('state', '=', 'validate'),  # Filter by the state of the leave request (approved)
                    ('holiday_status_id.name', '!=', 'Ferien'),  # Filter by the type of leave (Sick Leave)
                    ('holiday_status_id.name', '!=', 'Compensatory Days')  # Filter by the type of leave (Sick Leave)
                ])


                # Define a list to store approved sick leaves details
                approved_sick_leaves_details = []

            # Iterate over the approved leave requests and append details to the list
                for leave in approved_sick_leaves:
                    # Calculate the number of days for the leave request
                    # duration_days = (leave.request_date_to - leave.request_date_from).days + 1
                    duration_days = leave.number_of_days_display
                    # Append details to the list
                    approved_sick_leaves_details.append({
                        'from_date': leave.request_date_from,
                        'to_date': leave.request_date_to,
                        'days': duration_days,
                        'description': leave.holiday_status_id.name
                    })

                employee_data_datails.append({
                    'current': i,
                    'current_year_total_entitlement': round(current_year_total_entitlement, 2),
                    'current_year_total_taken_holidays': round(current_year_total_taken_holidays, 2),
                    'remaining_holidays': round(remaining_holidays, 2),
                    'approved_holidays_details': approved_holidays_details,
                    'approved_sick_leaves_details': approved_sick_leaves_details,
                })
            employees_list.append({
                'employee': record,
                'yearly_hours_details': yearly_hours_details,
                # Previous Year Data
                'previous_year': previous_year,
                'previous_year_entitlement': round(previous_year_entitlement, 2),
                'previous_year_total_taken_holidays': round(previous_year_total_taken_holidays, 2),
                'previous_year_remaining_holidays': round(previous_year_remaining_holidays, 2),
                'previous_years_extra_hours': round(previous_years_extra_hours, 2),
                # Current Year Data
                'current_year': current_year,
                'employee_data_datails':employee_data_datails,
            })

        return {
            'docs': docs,
            'records': employees_list,  # complete records
        }

    def _get_employees_days_per_allocation(self, employee_ids, date=None, date_to=None):
        # if not date:
        #     date = fields.Date.to_date(self.env.context.get('default_date_from')) or fields.Date.context_today(self)

        leaves_domain = [
            ('employee_id', 'in', employee_ids),
            ('date_from', '>=', date),
            ('date_to', '<=', date_to),
            ('state', '=', 'validate'),
        ]
        # if self.env.context.get("ignore_future"):
        #     leaves_domain.append(('date_from', '<=', date))
        leaves = self.env['hr.leave'].search(leaves_domain)

        allocations = self.env['hr.leave.allocation'].with_context(active_test=False).search([
            ('employee_id', 'in', employee_ids),
            ('date_from', '>=', date),
            ('date_to', '<=', date_to),
            ('state', 'in', ['validate']),
        ])

        # The allocation_employees dictionary groups the allocations based on the employee and the holiday type
        # The structure is the following:
        # - KEYS:
        # allocation_employees
        #   |--employee_id
        #      |--holiday_status_id
        # - VALUES:
        # Intervals with the start and end date of each allocation and associated allocations within this interval
        allocation_employees = defaultdict(lambda: defaultdict(list))

        ### Creation of the allocation intervals ###
        for holiday_status_id in allocations.holiday_status_id:
            for employee_id in employee_ids:
                allocation_intervals = Intervals([(
                    fields.datetime.combine(allocation.date_from, time.min),
                    fields.datetime.combine(allocation.date_to or datetime.date.max, time.max),
                    allocation)
                    for allocation in allocations.filtered(
                        lambda allocation: allocation.employee_id.id == employee_id and allocation.holiday_status_id == holiday_status_id)])

                allocation_employees[employee_id][holiday_status_id] = allocation_intervals

        # The leave_employees dictionary groups the leavess based on the employee and the holiday type
        # The structure is the following:
        # - KEYS:
        # leave_employees
        #   |--employee_id
        #      |--holiday_status_id
        # - VALUES:
        # Intervals with the start and end date of each leave and associated leave within this interval
        leaves_employees = defaultdict(lambda: defaultdict(list))
        leave_intervals = []

        ### Creation of the leave intervals ###
        if leaves:
            for holiday_status_id in leaves.holiday_status_id:
                for employee_id in employee_ids:
                    leave_intervals = Intervals([(
                        fields.datetime.combine(leave.date_from, time.min),
                        fields.datetime.combine(leave.date_to, time.max),
                        leave)
                        for leave in leaves.filtered(lambda leave: leave.employee_id.id == employee_id and leave.holiday_status_id == holiday_status_id)])

                    leaves_employees[employee_id][holiday_status_id] = leave_intervals

        # allocation_days_consumed is a dictionary to map the number of days/hours of leaves taken per allocation
        # The structure is the following:
        # - KEYS:
        # allocation_days_consumed
        #  |--employee_id
        #      |--holiday_status_id
        #          |--allocation
        #              |--virtual_leaves_taken
        #              |--leaves_taken
        #              |--virtual_remaining_leaves
        #              |--remaining_leaves
        #              |--max_leaves
        #              |--closest_allocation_to_expire
        # - VALUES:
        # Integer representing the number of (virtual) remaining leaves, (virtual) leaves taken or max leaves for each allocation.
        # The unit is in hour or days depending on the leave type request unit
        allocations_days_consumed = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))

        company_domain = [('company_id', 'in', list(set(self.env.company.ids + self.env.context.get('allowed_company_ids', []))))]

        ### Existing leaves assigned to allocations ###
        if leaves_employees:
            for employee_id, leaves_interval_by_status in leaves_employees.items():
                for holiday_status_id in leaves_interval_by_status:
                    days_consumed = allocations_days_consumed[employee_id][holiday_status_id]
                    if allocation_employees[employee_id][holiday_status_id]:
                        allocations = allocation_employees[employee_id][holiday_status_id] & leaves_interval_by_status[holiday_status_id]
                        available_allocations = self.env['hr.leave.allocation']
                        for allocation_interval in allocations._items:
                            available_allocations |= allocation_interval[2]
                        # Consume the allocations that are close to expiration first
                        sorted_available_allocations = available_allocations.filtered('date_to').sorted(key='date_to')
                        sorted_available_allocations += available_allocations.filtered(lambda allocation: not allocation.date_to)
                        leave_intervals = leaves_interval_by_status[holiday_status_id]._items
                        sorted_allocations_with_remaining_leaves = self.env['hr.leave.allocation']
                        for leave_interval in leave_intervals:
                            leaves = leave_interval[2]
                            for leave in leaves:
                                if leave.leave_type_request_unit in ['day', 'half_day']:
                                    leave_duration = leave.number_of_days
                                    leave_unit = 'days'
                                else:
                                    leave_duration = leave.number_of_hours_display
                                    leave_unit = 'hours'
                                if holiday_status_id.requires_allocation != 'no':
                                    for available_allocation in sorted_available_allocations:
                                        if (available_allocation.date_to and available_allocation.date_to < leave.date_from.date()) \
                                                or (available_allocation.date_from > leave.date_to.date()):
                                            continue
                                        virtual_remaining_leaves = (
                                                                       available_allocation.number_of_days if leave_unit == 'days' else available_allocation.number_of_hours_display) - \
                                                                   allocations_days_consumed[employee_id][holiday_status_id][available_allocation][
                                                                       'virtual_leaves_taken']
                                        max_leaves = min(virtual_remaining_leaves, leave_duration)
                                        days_consumed[available_allocation]['virtual_leaves_taken'] += max_leaves
                                        if leave.state == 'validate':
                                            days_consumed[available_allocation]['leaves_taken'] += max_leaves
                                        leave_duration -= max_leaves
                                        # Check valid allocations with still availabe leaves on it
                                        if days_consumed[available_allocation][
                                            'virtual_remaining_leaves'] > 0 and available_allocation.date_to and available_allocation.date_to > date:
                                            sorted_allocations_with_remaining_leaves |= available_allocation
                                    if leave_duration > 0:
                                        # There are not enough allocation for the number of leaves
                                        days_consumed[False]['virtual_remaining_leaves'] -= leave_duration
                                else:
                                    days_consumed[False]['virtual_leaves_taken'] += leave_duration
                                    if leave.state == 'validate':
                                        days_consumed[False]['leaves_taken'] += leave_duration
                        # no need to sort the allocations again
                        allocations_days_consumed[employee_id][holiday_status_id][False]['closest_allocation_to_expire'] = \
                            sorted_allocations_with_remaining_leaves[0] if sorted_allocations_with_remaining_leaves else False

        # Future available leaves
        future_allocations_date_from = fields.datetime.combine(date, time.min)
        future_allocations_date_to = fields.datetime.combine(date, time.max) + timedelta(days=5 * 365)
        for employee_id, allocation_intervals_by_status in allocation_employees.items():
            employee = self.env['hr.employee'].browse(employee_id)
            for holiday_status_id, intervals in allocation_intervals_by_status.items():
                if not intervals:
                    continue
                future_allocation_intervals = intervals & Intervals([(
                    future_allocations_date_from,
                    future_allocations_date_to,
                    self.env['hr.leave'])])
                search_date = date
                closest_allocations = self.env['hr.leave.allocation']
                for interval in intervals._items:
                    closest_allocations |= interval[2]
                allocations_with_remaining_leaves = self.env['hr.leave.allocation']
                for interval_from, interval_to, interval_allocations in future_allocation_intervals._items:
                    if interval_from.date() > search_date:
                        continue
                    interval_allocations = interval_allocations.filtered('active')
                    if not interval_allocations:
                        continue
                    # If no end date to the allocation, consider the number of days remaining as infinite
                    employee_quantity_available = (
                        employee._get_work_days_data_batch(interval_from, interval_to, compute_leaves=False, domain=company_domain)[employee_id]
                        if interval_to != future_allocations_date_to
                        else {'days': float('inf'), 'hours': float('inf')}
                    )
                    for allocation in interval_allocations:
                        if allocation.date_from > search_date:
                            continue
                        days_consumed = allocations_days_consumed[employee_id][holiday_status_id][allocation]
                        if allocation.type_request_unit in ['day', 'half_day']:
                            quantity_available = employee_quantity_available['days']
                            remaining_days_allocation = (allocation.number_of_days - days_consumed['virtual_leaves_taken'])
                        else:
                            quantity_available = employee_quantity_available['hours']
                            remaining_days_allocation = (allocation.number_of_hours_display - days_consumed['virtual_leaves_taken'])
                        if quantity_available <= remaining_days_allocation:
                            search_date = interval_to.date() + timedelta(days=1)
                        days_consumed['virtual_remaining_leaves'] += min(quantity_available, remaining_days_allocation)
                        days_consumed['max_leaves'] = allocation.number_of_days if allocation.type_request_unit in ['day',
                                                                                                                    'half_day'] else allocation.number_of_hours_display
                        days_consumed['remaining_leaves'] = days_consumed['max_leaves'] - days_consumed['leaves_taken']
                        if remaining_days_allocation >= quantity_available:
                            break
                        # Check valid allocations with still availabe leaves on it
                        if days_consumed['virtual_remaining_leaves'] > 0 and allocation.date_to and allocation.date_to > date:
                            allocations_with_remaining_leaves |= allocation
                allocations_sorted = sorted(allocations_with_remaining_leaves, key=lambda a: a.date_to)
                allocations_days_consumed[employee_id][holiday_status_id][False]['closest_allocation_to_expire'] = allocations_sorted[
                    0] if allocations_sorted else False
        return allocations_days_consumed
