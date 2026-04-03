{
    'name': 'Sales Target',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage monthly sales targets per user',
    'description': """
        Sales Target 
        =======================
        • Assign sales targets to users
        • Monthly & yearly targets
        • Track target amounts per user
    """,
    'author': 'Techvizor',
    'depends': [
        'base', 'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_target_views.xml',
        
    ],
    'assets': {
        'web.assets_backend': [],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
