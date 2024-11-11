# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    print_product_image = fields.Boolean(string='Print Product Image on Report')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_128 = fields.Image(string='Image', related='product_id.image_128')