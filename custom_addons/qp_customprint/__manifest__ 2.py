# -*- coding: utf-8 -*-
{
    'name': 'QP Print Solution',
    'summary': 'enable product pictures on quotation ans sales order',
    'version': '17.24.12',
    'sequence': 1,
    'category': 'Sales/Sales',
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'depends': [
        'sale', 'account', 'purchase'
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'report/sale_report_templates.xml',
        'report/sale_portal_templates.xml',
        'report/invoice_report_templates.xml',
        'report/purchase_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
