# -*- coding: utf-8 -*-
{
    'name': "Payroll Extension",

    'summary': """
    some addation in payroll module
        """,

    'description': """
        Long description of module's purpose
    """,

    'description': """Make overtime possible plus and minus Values""",
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.23',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
