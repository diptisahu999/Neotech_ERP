from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    terms_condition_id = fields.Many2one("terms.and.conditions", string="Terms and Condition")
    additional_notes = fields.Html(string="Additional Notes")

    @api.onchange("terms_condition_id")
    def _onchange_terms_condition_id(self):
        if self.terms_condition_id:
            self.note = self.terms_condition_id.terms_condition
        else:
            self.note = False   # 🔥 CLEAR the bottom note

    def action_apply_terms(self):
        for record in self:
            if record.terms_condition_id:
                record.note = record.terms_condition_id.terms_condition
            else:
                record.note = False

    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            if any(picking.state not in ['done', 'cancel'] for picking in order.picking_ids):
                raise ValidationError(_("You cannot create an invoice until all delivery orders are validated."))
        return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)

    def action_open_create_invoice_wizard(self):
        for order in self:
            # Check for availability: if any picking is not yet ready or done, block
            if any(picking.state not in ['assigned', 'done', 'cancel'] for picking in order.picking_ids):
                # Specific check for availability
                for picking in order.picking_ids:
                    if picking.state == 'confirmed' and picking.products_availability_state == 'unavailable':
                         raise ValidationError(_("You cannot create an invoice because some products are not available in the delivery order."))
                raise ValidationError(_("You cannot create an invoice because delivery availability is not confirmed or checked."))
        
        # Return the standard wizard action
        action = self.env.ref('sale.action_view_sale_advance_payment_inv').read()[0]
        action['context'] = self._context.copy()
        return action
