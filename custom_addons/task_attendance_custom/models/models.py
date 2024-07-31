from odoo import models, _, exceptions
from datetime import datetime


class HrEmployee(models.Model):
  _inherit = 'hr.employee'

  def _attendance_action_change(self):

    # task_lst = ' '.join([task.name for task in tasks])
    # project_set = set([task.project_id.name for task in tasks])
    # project_set = ' '.join(project_set)

    # if len(tasks) > 0:
    #   raise exceptions.UserError(_('You have Running tasks for: %s in projects :%s', task_lst, project_set))

    tasks = self.env['project.task'].sudo().search([('log_action', '=', 'working'),
                                                    ('user_ids', 'in', self._uid)])
    for task in tasks:
      for rec in task.timesheet_ids:
        attendance = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id),
                                                       ('check_out', '=', False)],
                                                      limit=1)
        if rec.employee_id.user_id.id == self._uid and rec.name == 'Working...' and attendance:
          # if project_admin:

          #   activity_vals.append({
          #       'user_id': project_admin,
          #       'res_id': task.id,
          #       'summary': _(f"Unstopped tasks-{rec.wk_name_get()}"),
          #       'res_model_id': self.env.ref('project.model_project_task').id,
          #   })
          #   self.env['mail.activity'].create(activity_vals)

          current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

          stop_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
          start_time = rec.start_time
          total_spent_hours = (stop_time - start_time).total_seconds() / 3600.0
          rec.write({
              'stop_time': datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
              'is_log_active': False,
              "name": rec.wk_name_get(),
              "unit_amount": total_spent_hours,
          })
          # task.write({"log_action": 'not_working'})

      if all(line.name != 'Working...' for line in task.timesheet_ids):
        task.write({"log_action": 'not_working'})

    return super()._attendance_action_change()
