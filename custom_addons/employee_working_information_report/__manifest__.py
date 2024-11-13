# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Working Information Report in Odoo',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'HR Employee Working Information Report in Odoo',
    'description': """HR Employee Working Information Report in Odoo""",
    'author': "Qplexity Solutions GmbH",
    "website": "https://www.qplexity.com",
    'depends': ['base', 'hr', 'hr_holidays', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard.xml',
        'report/report.xml',
    ],
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
