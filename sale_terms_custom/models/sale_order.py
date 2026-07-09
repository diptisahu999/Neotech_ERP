from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    terms_condition_id = fields.Many2one("terms.and.conditions", string="Terms and Condition")
    additional_notes = fields.Html(string="Additional Notes")
    remarks_id = fields.Many2one(
        "sale.remarks",
        string="Remarks"
    )
    remarks_section = fields.Html(string="Remarks Section", compute="_compute_sections", store=True)
    terms_section = fields.Html(string="Terms & Conditions Section", compute="_compute_sections", store=True)

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        super(SaleOrder, self)._compute_pricelist_id()
        for order in self:
            if not order.partner_id:
                inr_pricelist = self.env['product.pricelist'].search([('currency_id.name', '=', 'INR')], limit=1)
                if inr_pricelist:
                    order.pricelist_id = inr_pricelist.id

    @api.depends("remarks_id", "terms_condition_id")
    def _compute_sections(self):
        for record in self:
            record.remarks_section = record.remarks_id.remarks if record.remarks_id else False
            record.terms_section = record.terms_condition_id.terms_condition if record.terms_condition_id else False

    @api.onchange("terms_condition_id", "remarks_id")
    def _onchange_remarks_or_terms(self):
        remarks_content = self.remarks_id.remarks if self.remarks_id else ""
        terms_content = self.terms_condition_id.terms_condition if self.terms_condition_id else ""
        
        # Combine for the standard note field (used in reports)

        combined_note = ""
        if remarks_content:
            combined_note += remarks_content
        if terms_content:
            if combined_note:
                combined_note += "<br/>"
            combined_note += terms_content
            
        self.note = combined_note

    def action_apply_terms(self):
        for record in self:
            record._onchange_remarks_or_terms()



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



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(digits=(16, 2))
    price_subtotal = fields.Float(digits=(16, 2))