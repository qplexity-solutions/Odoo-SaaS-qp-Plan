{
    'name':
        "Attendance Cleaner",
    'summary':
        """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author':
        "",
    'website':
        "http://qplexity.ch",
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
        'hr_attendance',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/stop_task_cron.xml'
    ],
    # only loaded in demonstration mode
}
