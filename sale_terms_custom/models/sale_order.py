from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    terms_condition_id = fields.Many2one("terms.and.conditions", string="Terms and Condition")
    additional_notes = fields.Html(string="Additional Notes")

    @api.onchange("terms_condition_id")
    def _onchange_terms_condition_id(self):
        if self.terms_condition_id:
            self.note = self.terms_condition_id.terms_condition

    def action_apply_terms(self):
        for record in self:
            if record.terms_condition_id:
                record.note = record.terms_condition_id.terms_condition
