# -*- coding: utf-8 -*-

{
    'name': 'Polish fiscal printer driver for POS Box',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'website': 'https://www.litxservice.pl',
    'summary': 'Hardware Driver for Polish fiscal printers (currently Novitus XML Protocol)',
    'description': """
Polish fiscal printer driver
=============================

This modules allows printing to Novitus fiscal printers. 

""",
    'depends': ['hw_proxy'],
    'external_dependencies': {
        'python' : [
            'pyserial', 
            'litex.novitus_xml', 
            'litex.novitus'
        ],
    },
    'installable': False,
}
