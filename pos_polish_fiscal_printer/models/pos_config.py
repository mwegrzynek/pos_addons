# -*- coding: utf-8 -*-
from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pfp_print_through = fields.Boolean(
        string='Polish Fiscal Printer'
    )

    pfp_cashdrawer = fields.Boolean(
        string='PFP Cashdrawer'
    )
