{
    "name": "Sale Custom Terms Button",
    "version": "1.0.0",
    "author": "Antigravity",
    "depends": ["sale", "sale_management", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/terms_condition_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
