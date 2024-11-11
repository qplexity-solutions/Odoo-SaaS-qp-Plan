# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    print_product_image = fields.Boolean(string='Print Product Image on Report')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    image_128 = fields.Image(string='Image', related='product_id.image_128')
