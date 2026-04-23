{
    "name": "Purchase Report",
    "version": "1.0.0",
    "summary": "Purchase Report",
    'author': "Techvizoe",
    "depends": ["purchase"],
    "data": [
        # Data
        "data/report_paperformat_data.xml",
        # Reports
        "reports/purchase_order_report_action.xml",
    ],
    "application": True,
    "sequence": 1,
    "installable": True,
    "auto_install": False,
}
