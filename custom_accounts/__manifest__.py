{
    'name'    : 'Custom Accounts',
    'version' : '1.0',
    'summary' : 'Custom Accounts Module Opening Balance and Journal Entry Import, opening debit and credit fields',
    'category': 'Accounting',
    'author'  : 'Techvizor',
    'description': """
        1. This module adds opening debit and credit fields to account.account model and allows importing journal entries from a CSV file.
        2. This module also provides a wizard for creating opening balance entries.
    """,
    'depends': ['account', 'base_accounting_kit'],
    'data'   : [
        'security/ir.model.access.csv',
        'views/opening_balance_wizard_view.xml',
        'views/account_settings_view.xml',
        'views/hide_accounting_reports_view.xml',
    ],
    'installable': True,
}