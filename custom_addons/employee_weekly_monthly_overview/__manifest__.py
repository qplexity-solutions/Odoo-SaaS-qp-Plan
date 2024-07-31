# -*- coding: utf-8 -*-
{
    'name': 'Employee Weekly & Monthly Overview',
    'version': '0.1',
    'category': 'Human Resources',
    'summary': 'Employee Weekly & Monthly Overview',
    'description': """It extracts information about the employees, year, month, and overview type (weekly or monthly) from the context.
        It browses through the hr.employee model to fetch details of the specified employees.
        For each employee, it calculates and aggregates hours' details based on the specified year, month, and overview type.
        It constructs a list of employee details, including hours worked, to be displayed in the report.
        The report can generate information either monthly or weekly, based on the overview_type parameter.
        It utilizes Python's datetime module to handle date calculations and calendar module to get the number of days in a month.
        The report is designed to provide insights into employee activities, facilitating analysis and decision-making within the organization.
    """,
    'author': "Siddiq Chauhdry | MarkhorTech",
    "website": "https://www.markhortech.pk",
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
