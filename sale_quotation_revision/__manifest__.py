{
    'name': 'Sale Quotation Revision',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Track revisions of sales quotations',
    'description': """
        This module allows users to create revisions of sales quotations.
        When a revision is created, the quotation is duplicated with a new revision number (e.g., S00031-R1),
        and the original quotation is canceled.
    """,
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
