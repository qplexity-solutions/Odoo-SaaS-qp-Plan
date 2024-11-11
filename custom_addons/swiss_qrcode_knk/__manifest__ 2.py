# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Swiss QR bill',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'summary': '''
        QR-bill for payment slips in Switzerland | QR Code | Swiss QR code | swiss QR payment
    ''',
    'description': '''
        This module will add a QR code to invoice
        User can able to scan the QR code and able to pay the invoice
    ''',
    'depends': [
        'l10n_ch',
        'sale_management',
    ],
    'external_dependencies': {
        'python': ['pypng', 'pyqrcode']
    },
    'data': [
        'reports/report_invoice.xml',
        'reports/reports.xml',
        'views/account_invoice.xml',
        'views/res_partner_bank.xml',
        'views/sale_order_view.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'currency': 'EUR',
    'price': 50
}
