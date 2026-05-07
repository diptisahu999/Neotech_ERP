{
    'name': 'Tag Search & Delete Assessment',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Control Search More visibility and add Delete button on Tags',
    'description': """
        - Adds a delete button (trash icon) to tag list views.
        - Adds a user-wise permission to hide 'Search More...' in tag fields.
    """,
    'author': 'Techvizor',
    'depends': ['base', 'crm', 'contacts', 'sales_team'],
    'data': [
        'views/res_users_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/tag_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
