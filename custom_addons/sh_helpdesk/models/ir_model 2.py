# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        for rec in res:
            if rec.res_model and rec.res_id and rec.res_model == 'sh.helpdesk.ticket':
                helpdesk = self.env['sh.helpdesk.ticket'].browse(rec.res_id)
                helpdesk.attachment_ids = [(4, res.id,0)]
                # rec.public = True
                
        return res

class IrModel(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def xmlid_to_res_model_res_id(self, xmlid, raise_if_not_found=False):
        return self._xmlid_to_res_model_res_id(xmlid, raise_if_not_found)[1]
        