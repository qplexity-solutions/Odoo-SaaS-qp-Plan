# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
from lxml import etree
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.base.models.ir_ui_view import NameManager
from odoo.addons.base.models import ir_ui_view

class IrActionReport(models.Model):
    _inherit="ir.actions.report"
    _description = 'Ir Action Report'

    group_ids = fields.Many2many('res.groups', string='Groups.')
    users_ids = fields.Many2many('res.users', string='Users')

class ModelAccess(models.Model):
    _inherit = 'ir.model.access'
    _description = 'Model Access'
    
    __cache_clearing_methods = set()

    @api.model
    def call_cache_clearing_methods(self):
        self.env.invalidate_all()
        self.env.registry.clear_cache()    # clear the cache of check function
        for model, method in self.__cache_clearing_methods:
            if model in self.env:
                getattr(self.env[model], method)()

class FieldConfiguration(models.Model):
    _name = 'field.config'
    _description = 'Field Configuration'

    config_fields_id = fields.Many2one('ir.model', string='Fields')
    fields_id = fields.Many2one('ir.model.fields', string='Field')
    name = fields.Char(string='Technical Name', related='fields_id.name')
    group_ids = fields.Many2many('res.groups', string='Groups ')
    readonly = fields.Boolean(string='Readonly')
    invisible = fields.Boolean(string='Invisible')

    def write(self, vals):
        if self.ids:
            self.env['ir.model.access'].call_cache_clearing_methods()
            for rec in self:
                if rec.readonly == True:
                    module_id=self.env['ir.module.module'].search([('name','=','bi_hide_show_menu_app')])
                    module_id.button_immediate_upgrade()

                elif rec.invisible == True:
                    module_id=self.env['ir.module.module'].search([('name','=','bi_hide_show_menu_app')])
                    module_id.button_immediate_upgrade()
                
                else:
                    module_id=self.env['ir.module.module'].search([('name','=','bi_hide_show_menu_app')])
                    module_id.button_immediate_upgrade()
        
        return super(FieldConfiguration, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(FieldConfiguration, self).create(vals_list)
        if res.ids:
            self.env['ir.model.access'].call_cache_clearing_methods()
        return res

    def unlink(self):
        if self.ids:
            self.env['ir.model.access'].call_cache_clearing_methods()
        return super(FieldConfiguration, self).unlink()






class IrModel(models.Model):
    _inherit= "ir.model"
    _description = 'Ir Model'

    field_config_id = fields.One2many('field.config','config_fields_id', string='Field Config')

    
class View(models.Model):
    _inherit = 'ir.ui.view'
    _description = 'View'

    def _postprocess_tag_field(self, node, name_manager, node_info):
        result = super(View, self)._postprocess_tag_field(node, name_manager, node_info)
        model_name = name_manager.model._name
        model_id = self.env['ir.model'].sudo().search([('model', '=', model_name)],limit=1)
        if node.tag == 'field' and model_id.field_config_id:
            field_name = node.get("name")
            for field_line in model_id.field_config_id.filtered(lambda field_line : not field_line.group_ids and field_line.fields_id.name == field_name and field_line.fields_id.model == model_id.model):
                if field_line.invisible == True:
                    node.set('invisible', '1')
                if field_line.readonly == True:
                    node.set('readonly', '1')
            for field_line in model_id.field_config_id.filtered(lambda field_line : field_line.group_ids and field_line.fields_id.name == field_name and field_line.fields_id.model == model_id.model):
                if field_line.group_ids.filtered(lambda group : group.users and group.users in [self.env.user]):
                    if field_line.invisible == True:
                        node.set('invisible', '1') 
                    if field_line.readonly == True:
                        node.set('readonly', '1')

        return result