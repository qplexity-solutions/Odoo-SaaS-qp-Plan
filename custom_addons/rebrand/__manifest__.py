# -*- coding: utf-8 -*-
{
    'name': "Odoo Rebranding",
    'author': "Odoo Pro 365",
    'website': "https://www.odoopro365.com",
    "support": "odoostar@outlook.com",
    "license": "OPL-1",
    'category': 'Website/Website',
    'summary': """
        Rebrand odoo community""",

    'description': """
        Remove odoo logo from website
        Remove odoo logo from eCommerce
        Remove odoo logo from Portal
        # Remove odoo logo from mails
        Change invoicing menue to accounting
        Full Features Accounting App
        Multi level security for admin and accounting
    """,
    'version': '16.0',
    'depends': ['base', 'website', 'account'],

    'application': True,
    'data': [
        # 'security/ir.model.access.csv',
        'security/groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],

    "images": ["static/description/background.png", ],
    "auto_install": False,
    'application': True,
    "installable": True,
    "price": 30,
    "currency": "EUR"
}
