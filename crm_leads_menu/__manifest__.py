{
    'name': 'CRM Leads Menu',
    'version': '1.0',
    'description': """
        Adds separate Leads menu in CRM, custom pipeline stages,
        salesperson isolation (own records only), and lead distribution wizard.
    """,
    'author': 'Techvizor',
    'category': 'CRM',
    'depends': ['crm', 'sale', 'crm_iap_mine'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/crm_stage_data.xml',
        'views/crm_leads_menu.xml',
        'views/crm_lead_distribute_wizard_view.xml',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': False,
}