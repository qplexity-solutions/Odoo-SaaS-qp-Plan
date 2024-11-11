# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models
from .product_product import GENDER_LIST, SIZE_UOM


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_color = fields.Char(
        string='Color',
        compute='_compute_feed_color',
        inverse='_inverse_feed_color',
        store=True,
    )
    feed_size = fields.Char(
        string='Size',
        compute='_compute_feed_size',
        inverse='_inverse_feed_size',
        store=True,
    )
    feed_material = fields.Char(
        string='Material',
        compute='_compute_feed_material',
        inverse='_inverse_feed_material',
        store=True,
    )
    feed_pattern = fields.Char(
        string='Pattern',
        compute='_compute_feed_pattern',
        inverse='_inverse_feed_pattern',
        store=True,
    )
    feed_gender = fields.Selection(
        string='Gender',
        selection=GENDER_LIST,
        compute='_compute_feed_gender',
        inverse='_inverse_feed_gender',
        store=True,
    )
    feed_length = fields.Float(
        string='Product Length',
        compute='_compute_feed_length',
        inverse='_inverse_feed_length',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_width = fields.Float(
        string='Product Width',
        compute='_compute_feed_width',
        inverse='_inverse_feed_width',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_height = fields.Float(
        string='Product Height',
        compute='_compute_feed_height',
        inverse='_inverse_feed_height',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_size_uom = fields.Selection(
        string='UOM',
        selection=SIZE_UOM,
        help='Unit of Measure.',
        compute='_compute_feed_size_uom',
        inverse='_inverse_feed_size_uom',
        store=True,
    )
    feed_size_system = fields.Selection(
        selection=[
            ('AU', 'AU'),
            ('BR', 'BR'),
            ('CN', 'CN'),
            ('DE', 'DE'),
            ('EU', 'EU'),
            ('FR', 'FR'),
            ('IT', 'IT'),
            ('JP', 'JP'),
            ('MEX', 'MEX'),
            ('UK', 'UK'),
            ('US', 'US'),
        ],
        string='Size System',
    )
    feed_expiration_date = fields.Date(
        string='Expiration Date',
        compute='_compute_feed_expiration_date',
        inverse='_inverse_feed_expiration_date',
        help="Product expiration. If the product is expired, it won't be shown in the feed recipient side.",
        store=True,
    )

    @api.depends('product_variant_ids.feed_gtin')
    def _compute_feed_gtin(self):
        self._compute_template_field_from_variant_field('feed_gtin')

    def _inverse_feed_gtin(self):
        self._set_product_variant_field('feed_gtin')

    @api.depends('product_variant_ids.feed_mpn')
    def _compute_feed_mpn(self):
        self._compute_template_field_from_variant_field('feed_mpn')

    def _inverse_feed_mpn(self):
        self._set_product_variant_field('feed_mpn')

    @api.depends('product_variant_ids.feed_color')
    def _compute_feed_color(self):
        self._compute_template_field_from_variant_field('feed_color')

    def _inverse_feed_color(self):
        self._set_product_variant_field('feed_color')

    @api.depends('product_variant_ids.feed_size')
    def _compute_feed_size(self):
        self._compute_template_field_from_variant_field('feed_size')

    def _inverse_feed_size(self):
        self._set_product_variant_field('feed_size')

    @api.depends('product_variant_ids.feed_material')
    def _compute_feed_material(self):
        self._compute_template_field_from_variant_field('feed_material')

    def _inverse_feed_material(self):
        self._set_product_variant_field('feed_material')

    @api.depends('product_variant_ids.feed_pattern')
    def _compute_feed_pattern(self):
        self._compute_template_field_from_variant_field('feed_pattern')

    def _inverse_feed_pattern(self):
        self._set_product_variant_field('feed_pattern')

    @api.depends('product_variant_ids.feed_gender')
    def _compute_feed_gender(self):
        self._compute_template_field_from_variant_field('feed_gender')

    def _inverse_feed_gender(self):
        self._set_product_variant_field('feed_gender')

    @api.depends('product_variant_ids.feed_length')
    def _compute_feed_length(self):
        self._compute_template_field_from_variant_field('feed_length')

    def _inverse_feed_length(self):
        self._set_product_variant_field('feed_length')

    @api.depends('product_variant_ids.feed_width')
    def _compute_feed_width(self):
        self._compute_template_field_from_variant_field('feed_width')

    def _inverse_feed_width(self):
        self._set_product_variant_field('feed_width')

    @api.depends('product_variant_ids.feed_height')
    def _compute_feed_height(self):
        self._compute_template_field_from_variant_field('feed_height')

    def _inverse_feed_height(self):
        self._set_product_variant_field('feed_height')

    @api.depends('product_variant_ids.feed_size_uom')
    def _compute_feed_size_uom(self):
        self._compute_template_field_from_variant_field('feed_size_uom')

    def _inverse_feed_size_uom(self):
        self._set_product_variant_field('feed_size_uom')

    @api.depends('product_variant_ids.feed_expiration_date')
    def _compute_feed_expiration_date(self):
        self._compute_template_field_from_variant_field('feed_expiration_date')

    def _inverse_feed_expiration_date(self):
        self._set_product_variant_field('feed_expiration_date')
