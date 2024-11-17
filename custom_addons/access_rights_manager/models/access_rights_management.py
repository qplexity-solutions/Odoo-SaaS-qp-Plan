from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.http import request


class access_management(models.Model):
    _name = 'access.rights.management'
    _description = "Access rights Management"

    name = fields.Char('Name')
    user_ids = fields.Many2many('res.users', 'access_management_users_rel_ah', 'access_rights_management_id', 'user_id',
                                'Users')

    readonly = fields.Boolean('Read-Only')
    active = fields.Boolean('Active', default=True)

    hide_menu_ids = fields.Many2many('menu.item', 'access_management_menu_rel_ah', 'access_rights_management_id', 'menu_id',
                                     'Hide Menu')
    hide_field_ids = fields.One2many('hide.field', 'access_rights_management_id', 'Hide Field', copy=True)

    remove_action_ids = fields.One2many('remove.action', 'access_rights_management_id', 'Remove Action', copy=True)

    hide_view_nodes_ids = fields.One2many('hide.view.nodes', 'access_rights_management_id', 'Button/Tab Access', copy=True)

    self_module_menu_ids = fields.Many2many('ir.ui.menu', 'access_management_ir_ui_self_module_menu',
                                            'access_rights_management_id', 'menu_id', 'Self Module Menu',
                                            default=lambda self: self.env.ref('access_rights_manager.main_menu_access_rights_manager'))

    hide_chatter = fields.Boolean('Hide Chatter')



    disable_debug_mode = fields.Boolean('Disable Developer Mode')

    company_ids = fields.Many2many('res.company', 'access_management_comapnay_rel', 'access_rights_management_id',
                                   'company_id', 'Companies', required=True, default=lambda self: self.env.company)




    def toggle_active_value(self):
        for record in self:
            record.write({'active': not record.active})
        return True

    @api.model_create_multi
    def create(self, vals_list):
        res = super(access_management, self).create(vals_list)
        request.registry.clear_cache()
        for record in res:
            if record.readonly:
                for user in record.user_ids:
                    if user.has_group('base.group_system') or user.has_group('base.group_erp_manager'):
                        raise UserError(_('Admin user can not be set as a read-only..!'))
        return res

    def unlink(self):
        res = super(access_management, self).unlink()
        request.env.registry.clear_cache()
        return res

    def write(self, vals):
        res = super(access_management, self).write(vals)

        if self.readonly:
            for user in self.user_ids:
                if user.has_group('base.group_system') or user.has_group('base.group_erp_manager'):
                    raise UserError(_('Admin user can not be set as a read-only..!'))
        request.env.registry.clear_cache()
        return res



