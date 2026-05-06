from odoo import fields, models


class TermsAndConditions(models.Model):
    _name = "terms.and.conditions"
    _description = "Terms And Conditions"

    name = fields.Char("Name", required=True)
    terms_condition = fields.Html("Terms and Conditions")


class SaleRemarks(models.Model):
    _name = "sale.remarks"
    _description = "Sale Remarks"

    name = fields.Char("Name", required=True)
    remarks = fields.Html("Remarks")
