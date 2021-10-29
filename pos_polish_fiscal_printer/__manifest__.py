# -*- coding: utf-8 -*-

{
    'name': 'POS part of Polish fiscal printer driver',
    'version': '1.0',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'POS part of Polish fiscal printer driver',
    'description': """

POS part of Polish fiscal printer driver
""",
    'depends': ['point_of_sale'],
    'data': [
        'views/point_of_sale_assets.xml',
        'views/pos_payment_method_views.xml',
        'views/pos_config_views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'installable': True,
    'auto_install': False
}
