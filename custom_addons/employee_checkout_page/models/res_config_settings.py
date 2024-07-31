# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    total_projects_to_display = fields.Integer(
        string="Total Projetcs To Display",
        related="company_id.total_projects_to_display", readonly=False)
