# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    print_product_image = fields.Boolean(string='Print Product Image on Report')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    image_128 = fields.Image(string='Image', related='product_id.image_128')
