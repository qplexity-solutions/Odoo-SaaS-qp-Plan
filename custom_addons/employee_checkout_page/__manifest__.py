# -*- coding: utf-8 -*-
{
    'name': 'Employee Checkout Page Customisation',
    'summary': 'Employee Checkout Page Customisation',
    'description': """HR Check-In and Out Page Custom"",
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',

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
