# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    total_projects_to_display = fields.Integer(
        string="Total Projetcs To Display")
