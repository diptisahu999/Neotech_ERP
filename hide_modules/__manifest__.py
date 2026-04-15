{
    'name': 'Hide Modules',
    'version': '18.0.1.0.0',
    'description': """
        Hide specific modules for all users
            - Hide Employee menu for all users
            - Hide Link Tracker menu for all users
            - Hide Create Employee Button from Users under Settings for all users
    """,
    'category': 'Hidden',
    'author': 'Techvizor',
    'depends': [
        'hr', 
        'mass_mailing', 
        'mail'
    ],
    'data': [
        'security/groups.xml',
        'views/hide_employee_menu.xml',
    ],
    'installable': True,
    'application': False,
}