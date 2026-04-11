from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Product associated with the lead
    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )

    # Override the action_new_quotation method to pass the product from the opportunity to the sale order
    def action_new_quotation(self):
        action = super().action_new_quotation()

        if self.product_id:
            ctx = dict(action.get('context', {}))

            ctx.update({
                'default_order_line': [(0, 0, {
                    'product_id': self.product_id.id,
                    'product_uom_qty': 1,
                })]
            })

            action['context'] = ctx

        return action

    def action_distribute_to_salespersons(self):
        """Open the wizard to distribute this lead to 3–5 salespersons."""
        return {
            'name': 'Distribute Lead to Salespersons',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead.distribute.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Override the default_get method to pre-populate the order line with the product from the opportunity
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)

        opportunity_id = self.env.context.get('default_opportunity_id')

        if opportunity_id:
            opportunity = self.env['crm.lead'].browse(opportunity_id)

            if opportunity.product_id:
                vals['order_line'] = [(0, 0, {
                    'product_id': opportunity.product_id.id,
                    'product_uom_qty': 1,
                })]

        return vals
    
   
# set the default 'convert to opportunity' When open wizard on lead form view
class CrmLead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # ✅ Correct field + correct value
        res['name'] = 'convert'

        return res