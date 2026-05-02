{
    "name": "Sales Reports",
    "version": "1.0",
    "summary": "Custom sales reports and document upload functionality",
    "description": """
        1. New Custom sales reports and document upload functionality.
        2. Merge New custom quotation report with Document Upload.
        3. Send by mail functionality check who's login, accorading that send the mail -> Pick mail id from outgoing mail server configuration and send the mail.
    """,
    "depends": ["sale", "mail"],
    "data": [
        "data/report_paperformat_data.xml",
        "reports/custom_quotation_report.xml",
        "reports/new_quotation_report.xml",
        "views/sale_order_upload_document.xml"
    ],
    "installable": True,
    "application": False,
}