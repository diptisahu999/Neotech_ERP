{
    "name": "Inventory Customs",
    "version": "18.0.1.0",
    "category": "Inventory",
    "description": """
            Create separate stock overview list for:
                - Vendor stock (supplier locations)
                - Customer stock (customer locations)
                - This avoids confusion in On Hand Units.
    """,
    "author": "Techvizor",
    "depends": [
        "stock"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_overview.xml",
    ],
    "installable": True,
    "application": False,
}
