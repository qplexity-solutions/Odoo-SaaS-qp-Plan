# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Working Information Report in ',
    'version': '25.1',
    'category': 'Human Resources',
    'summary': 'HR Employee Working Information Report in ',
    'description': """HR Employee Working Information Report in """,
    'author': "Qplexity Solutions | GmbH",
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
