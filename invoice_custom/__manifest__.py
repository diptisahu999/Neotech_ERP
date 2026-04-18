{
    'name': 'Invoice custom',
    'version': '1.0',
    'description': """
        1. Add Project Id in Invoice.
        2. This module ensures that when a sale order linked to a project is invoiced,
            the project information is automatically transferred to the invoice. 
            This allows for better tracking and management of projects through the invoicing process.  
    """,
    'depends': ['sale', 'account', 'project', 'purchase'],
    'data': [
        "views/invoice_view.xml",
    ],
    'installable': True,
}