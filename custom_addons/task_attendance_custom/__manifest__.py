{
    'name':
        "Task Attendance Custom",
    'summary':
        """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'category':
        'Uncategorized',
    'license':
        'Other proprietary',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version':
        '16.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'project_start_stop',
        'project',
        'hr_timesheet',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
}
