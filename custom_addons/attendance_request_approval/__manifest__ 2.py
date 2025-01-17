# __manifest__.py
{
    'name': 'Attendance Request Manager with Approval Workflow',
    'author': 'qplexity solutions',
    'website': 'https://www.qplexity.com',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': '16.24.12.',
    'summary': 'Efficiently Manage Employee Attendance Requests with Advanced Approval Workflows',
    'description': """
Boost your HR operations with the Attendance Request Manager module, designed to streamline and automate the process of managing attendance modifications. This powerful tool empowers employees to request changes to their attendance records while ensuring robust oversight and approval mechanisms.

Key Features:
- Intuitive Request Submission: Employees can easily submit requests for check-in and check-out time adjustments.
- Automated Serial Numbers: Each request is automatically assigned a unique serial number for easy tracking and reference.
- Role-Based Access Control:
  - Employees: View and manage their own attendance requests.
  - Team Leads: Approve or reject requests from their team members.
  - Time Officers: Oversee and manage all attendance requests within the organization.
- Three-Stage Workflow: Requests progress through draft, approval, and rejection stages, ensuring a transparent and accountable process.
- Customizable Approval Process: Define specific user groups to handle different levels of approval.
- Seamless Integration: Fully integrates with Odoo HR and Attendance modules for a cohesive HR management experience.

Benefits:
- Enhance operational efficiency by reducing manual intervention and paperwork.
- Improve transparency and accountability in attendance management.
- Empower employees and team leads with a straightforward and effective approval process.

Install the Attendance Request Manager today and transform how your organization handles attendance modifications!
    """,
    'depends': ['base', 'hr', 'hr_attendance', 'mail'],
    'data': [
        'security/attendance_request_security.xml',
        'security/ir.model.access.csv',
        'data/attendance_request_data.xml',
        'views/attendance_request_views.xml',
        'views/attendance_request_wizard_views.xml',
        'views/attendance_request_menus.xml',
    ],
    'installable': True,
    'application': True,
}
