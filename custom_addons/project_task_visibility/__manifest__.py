# __manifest__.py
{
    'name': 'Project/Task Multi-Company',
    'summary': 'This module allows administrators to control the visibility of project tasks across companies',
    'description': """
        This module allows administrators to control the visibility of project tasks across companies 
         via a boolean toggle in the settings menu. 
        When activated, employees can see all projects and tasks from all companies
    """,
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',
    'depends': ['base', 'project'],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
}
