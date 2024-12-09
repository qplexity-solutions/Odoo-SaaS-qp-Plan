{
    'name':
        "Task Summary Custom",
    'summary':
        """
        Print Settings for Human Ressource""",
    'description': """HR Employee Working Information Report""",
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',
    'category':
        'Uncategorized',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic', 'hr_timesheet', 'project', 'hr','hr_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
}
