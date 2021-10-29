# -*- coding: utf-8 -*-

from odoo import fields, models

class POSPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pfp_fiscal_id = fields.Selection(
        selection=[
            ('card', 'card'),
            ('cheque', 'cheque'), 
            ('voucher', 'voucher'), 
            ('credit', 'credit'), 
            ('transfer', 'transfer'),
            ('account', 'account'), 
            ('foreign', 'foreign'),
            ('cash', 'cash'), 
            ('mobile', 'mobile'), 
            ('bon', 'bon')
        ],    
        string='Fiscal printer ID',
        default='cash',
        required=True
    )
