{
    'name': 'Project Task Library',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Add tasks to existing projects from a pre-defined library.',
    'description': """
        1. This module allows you to create a library of task templates with associated sub-task templates.
            You can then add tasks from your library to any existing project by clicking the "Add from Library" button inside the project form view.
        2. Create Project --> Validation for at least one product in order line and no delivery done.
        3. Added a new field "Project Created" in sale order to check whether project is created or not.
        4. Added a new field "Delivery Done" in project to check whether delivery is done or not.
        5. Added a new field "Due Days" in project to check due days of project.
        6. Added a new QA control wizard to check the quality of the project before marking it as done.
        7. Added a new field "QA Control" in project to check whether QA control is done or not.
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
        'wizard/qa_control_wizard_views.xml',
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