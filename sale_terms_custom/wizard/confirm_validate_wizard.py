from odoo import models, fields

# Confirmation popup before Validate on Delivery Order
class ConfirmValidateWizard(models.TransientModel):
    _name = 'confirm.validate.wizard'
    _description = 'Confirm Delivery Validation'

    picking_id = fields.Many2one('stock.picking', required=True)

    def action_confirm(self):
        return self.picking_id.with_context(skip_confirm=True).button_validate()