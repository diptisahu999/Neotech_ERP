{
    "name": "Sale Custom Terms Button",
    "version": "1.0.0",
    "summary": "Custom Button for Terms and Conditions in Sale Orders, with Confirmation Popup on Validate, and Quality Assurance Control",
    "description": """
        1. This module adds a custom button to the sale order form view to manage terms and conditions.
        2. Confirmation popup before Validate on Delivery Order
        3. Add Quality Assurance Control in Sale Order.
    """,
    "author": "Techvizor",
    "depends": ["sale", "sale_management", "sale_stock", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/terms_condition_views.xml",
        "views/sale_order_views.xml",
        "wizard/confirm_validate_wizard.xml",
        "views/qa_control_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
