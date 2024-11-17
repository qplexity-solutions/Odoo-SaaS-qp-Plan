from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        form_toolbar = res['views'].get('form', {}).get('toolbar') or False
        tree_toolbar = res['views'].get('list', {}).get('toolbar') or False
        remove_action = self.env['remove.action'].search(
            [('access_rights_management_id.company_ids', 'in', self.env.company.id),
             ('access_rights_management_id', 'in', self.env.user.access_rights_management_ids.ids),
             ('model_id.model', '=', self._name)])
        if form_toolbar or tree_toolbar:
            remove_server_action = remove_action.mapped('server_action_ids.action_id').ids
            remove_print_action = remove_action.mapped('report_action_ids.action_id').ids
        if form_toolbar:
            if res['views']['form']['toolbar'].get('action', False):
                action = [rec for rec in res['views']['form']['toolbar']['action'] if
                          rec.get('id', False) not in remove_server_action]
                res['views']['form']['toolbar']['action'] = action
            if res['views']['form']['toolbar'].get('print', False):
                prints = [rec for rec in res['views']['form']['toolbar']['print'] if
                          rec.get('id', False) not in remove_print_action]
                res['views']['form']['toolbar']['print'] = prints
        if tree_toolbar:
            if res['views']['list']['toolbar'].get('action', False):
                action = [rec for rec in res['views']['list']['toolbar']['action'] if
                          rec.get('id', False) not in remove_server_action]
                res['views']['list']['toolbar']['action'] = action
            if res['views']['list']['toolbar'].get('print', False):
                prints = [rec for rec in res['views']['list']['toolbar']['print'] if
                          rec.get('id', False) not in remove_print_action]
                res['views']['list']['toolbar']['print'] = prints
        return res

    @api.model
    def load_views(self, views, options=None):
        actions_and_prints = []
        for access in self.env['remove.action'].search([('access_rights_management_id.company_ids', 'in', self.env.company.id),
                                                        ('access_rights_management_id', 'in',
                                                         self.env.user.access_rights_management_ids.ids),
                                                        ('model_id.model', '=', self._name)]):
            actions_and_prints = actions_and_prints + access.mapped('report_action_ids.action_id').ids
            actions_and_prints = actions_and_prints + access.mapped('server_action_ids.action_id').ids

        res = super(BaseModel, self).load_views(views, options=options)

        if 'fields_views' in res.keys():
            for view in ['list', 'form']:
                if view in res['fields_views'].keys():
                    if 'toolbar' in res['fields_views'][view].keys():
                        if 'print' in res['fields_views'][view]['toolbar'].keys():
                            prints = res['fields_views'][view]['toolbar']['print'][:]
                            for pri in prints:
                                if pri['id'] in actions_and_prints:
                                    res['fields_views'][view]['toolbar']['print'].remove(pri)
                        if 'print' in res['fields_views'][view]['toolbar'].keys():
                            action = res['fields_views'][view]['toolbar']['action'][:]
                            for act in action:
                                if act['id'] in actions_and_prints:
                                    res['fields_views'][view]['toolbar']['action'].remove(act)
        return res

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        access_management_obj = self.env['access.rights.management']
        readonly_access_id = access_management_obj.search(
            [('company_ids', 'in', self.env.company.id), ('active', '=', True), ('user_ids', 'in', self.env.user.id),
             ('readonly', '=', True)])

        access_model_recs = self.env['remove.action'].search(
            [('access_rights_management_id.company_ids', 'in', self.env.company.id),
             ('access_rights_management_id.user_ids', 'in', self.env.user.id),
             ('access_rights_management_id.active', '=', True),
             ('model_id.model', '=', self._name)])
        if view_type == 'form':
            access_rights_management_id = access_management_obj.search([('company_ids', 'in', self.env.company.id),
                                                                 ('active', '=', True),
                                                                 ('user_ids', 'in', self.env.user.id),
                                                                 ('hide_chatter', '=', True)],
                                                                limit=1).id
            if access_rights_management_id:
                for div in arch.xpath("//div[@class='oe_chatter']"):
                    div.getparent().remove(div)

        if readonly_access_id:
            if view_type == 'form':
                arch.attrib.update({'create': 'false', 'delete': 'false', 'edit': 'false'})

            if view_type == 'tree':
                arch.attrib.update({'create': 'false', 'delete': 'false', 'edit': 'false'})

            if view_type == 'kanban':
                arch.attrib.update({'create': 'false', 'delete': 'false', 'edit': 'false'})

        else:

            if access_model_recs:
                delete = 'true'
                edit = 'true'
                create = 'true'
                duplicate = 'true'
                for access_model in access_model_recs:
                    if access_model.restrict_create:
                        create = 'false'
                    if access_model.restrict_edit:
                        edit = 'false'
                    if access_model.restrict_delete:
                        delete = 'false'
                    if access_model.restrict_duplicate:
                        duplicate = 'false'

                if view_type == 'form':
                    arch.attrib.update({'create': create, 'delete': delete, 'edit': edit, 'duplicate':duplicate})

                if view_type == 'tree':
                    arch.attrib.update({'create': create, 'delete': delete, 'edit': edit, 'duplicate':duplicate})

                if view_type == 'kanban':
                    arch.attrib.update({'create': create, 'delete': delete, 'edit': edit, 'duplicate':duplicate})

        return arch, view

