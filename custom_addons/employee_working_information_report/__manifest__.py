# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Working Information Report in Odoo',
    'summary': 'HR Employee Working Information Report in Odoo',
    'description': """HR Employee Working Information Report in Odoo""",
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',
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
