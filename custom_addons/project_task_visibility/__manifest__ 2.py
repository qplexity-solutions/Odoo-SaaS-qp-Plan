# __manifest__.py
{
    'name': 'Project/Task Multi-Company',
    'version': '1.0',
    'category': 'Project',
    'summary': 'This module allows administrators to control the visibility of project tasks across companies',
    'description': """
        This module allows administrators to control the visibility of project tasks across companies 
         via a boolean toggle in the settings menu. 
        When activated, employees can see all projects and tasks from all companies
    """,
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'depends': ['base', 'project'],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
}
