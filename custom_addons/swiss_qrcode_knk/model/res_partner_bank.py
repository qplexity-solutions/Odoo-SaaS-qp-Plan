# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    invoice_issuer_number = fields.Char('Invoice Issuer Number')
