from datetime import datetime
from odoo import models, fields, api, _
import logging


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def auto_stop_tasks(self):
        try:
            # Fetch project admin with sudo access
            project_admin = self.env['hr.employee'].sudo().search([('category_ids.name', '=', 'Zeitkontrolle')], limit=1).user_id
            if not project_admin:
                logging.warning("No project admin found in the 'Zeitkontrolle' category.")
                return

            # Fetch employees who haven't checked out with sudo access
            checked_in_employees = self.env['hr.employee'].sudo().search([('last_attendance_id.check_out', '=', False)])
            if not checked_in_employees:
                logging.info("No employees found who haven't checked out.")
                return

            action_date = fields.Datetime.now()
            attend_vals = []

            for emp in checked_in_employees.sudo():
                last_attendance = self.env['hr.attendance'].sudo().search([('employee_id', '=', emp.id)], order='create_date desc', limit=1)
                if last_attendance:
                    last_attendance.sudo().check_out = action_date
                    attend_vals.append({
                        'user_id': project_admin.id,
                        'res_id': emp.id,
                        'summary': _("Employees who didn't check out"),
                        'res_model_id': self.env.ref('hr.model_hr_employee').id,
                    })

            if attend_vals:
                self.env['mail.activity'].sudo().create(attend_vals)
                logging.info(f"Created mail activities for {len(attend_vals)} employees.")

            activity_vals = []

            for task in self.sudo().search([]):
                if task.log_action == 'working':
                    for rec in task.timesheet_ids:
                        current_time = fields.Datetime.now()
                        start_time = rec.start_time
                        if start_time:
                            total_spent_hours = (current_time - start_time).total_seconds() / 3600.0
                            rec.sudo().write({
                                'stop_time': current_time,
                                'is_log_active': False,
                                'unit_amount': total_spent_hours,
                            })
                            task.sudo().write({'log_action': 'not_working'})
                            activity_vals.append({
                                'user_id': project_admin.id,
                                'res_id': task.id,
                                'summary': _(f"Unstopped tasks - {rec.wk_name_get()}"),
                                'res_model_id': self.env.ref('project.model_project_task').id,
                            })

            if activity_vals:
                self.env['mail.activity'].sudo().create(activity_vals)
                logging.info(f"Created mail activities for {len(activity_vals)} tasks.")

        except Exception as e:
            logging.error(f"An error occurred in auto_stop_tasks: {e}", exc_info=True)
