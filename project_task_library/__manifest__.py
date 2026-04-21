{
    'name': 'Project Task Library',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Add tasks to existing projects from a pre-defined library.',
    'description': """
        1. This module allows you to create a library of task templates with associated sub-task templates.
            You can then add tasks from your library to any existing project by clicking the "Add from Library" button inside the project form view.
        2. Delivery Done status for Project (Due days).
        3. Added Create project button in sale order outer Header.
        4. Create Project --> Validation for at least one product in order line and no delivery done.
    """,
    'author': 'Pratham',
    'depends': [
        'project',
        'mail' ,
        'sale',
        'sale_project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/task_template_views.xml',
        'views/task_library_wizard_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/sale_order_views.xml',
        # 'views/sale_order_actions.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_task_library/static/src/css/project_task_library.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}