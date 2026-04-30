{
    'name': 'Partner Opening Balance',
    'version': '18.0.1.0',
    'category': 'Accounting',
    'summary': 'Opening Balance on Partner (Customer/Vendor)',
    'depends': ['account', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_partner_opening_balance/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}