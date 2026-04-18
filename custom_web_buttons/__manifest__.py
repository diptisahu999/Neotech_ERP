{
    'name': 'Custom Web Buttons',
    'version': '1.0',
    'category': 'Web',
    'summary': 'Changes Save and Discard icons back to text buttons',
    'description': """
        This module overrides the Odoo 18 Form Status Indicator to use text-based 
        Save and Discard buttons instead of icons, matching the classic Odoo style.
    """,
    'author': 'Antigravity',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'custom_web_buttons/static/src/views/form/form_status_indicator/form_status_indicator.xml',
            'custom_web_buttons/static/src/views/form/form_status_indicator/form_status_indicator.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
