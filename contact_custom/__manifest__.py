{
    'name': 'Contact Custom',
    'version': '18.0.1.0.0',
    'category': 'Customization',
    'summary': 'Customizations for Contacts',
    'description': """
        This module contains customizations for the Contact (res.partner) form.
        - Makes Phone field required for both Individual and Company.
        - Makes Tags field required for both Individual and Company.
    """,
    'depends': ['base', 'contacts', 'crm', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/bank_details_view.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
