from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deactivate_task_comp_rule = fields.Boolean(string='Activate / Deactivate')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        rule = self.env.ref('project.task_comp_rule', raise_if_not_found=False)
        res.update(
            deactivate_task_comp_rule=not rule.active if rule else False,
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        rule = self.env.ref('project.task_comp_rule', raise_if_not_found=False)
        if rule:
            rule.active = not self.deactivate_task_comp_rule
