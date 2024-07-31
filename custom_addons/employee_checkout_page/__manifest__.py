# -*- coding: utf-8 -*-
{
    'name': 'Employee Checkout Page Customisation',
    'version': '16.0.5',
    'summary': 'Employee Checkout Page Customisation',
    'description': """
        Employee Checkout Page Customisation
        Task ID: 3733197
    """,
    'category': 'Human Resources/Attendances',

    'author': 'Odoo PS',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',

    'depends': [
        'hr_attendance',
        'project',
        'hr_holidays',
    ],

    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'employee_checkout_page/static/src/xml/attendance.xml',
            'employee_checkout_page/static/src/js/my_attendances.js',
            'employee_checkout_page/static/src/js/kiosk_confirm.js',
            'employee_checkout_page/static/src/scss/hr_attendance.scss',
        ],
    },

    'installable': True,
    'application': False
}
