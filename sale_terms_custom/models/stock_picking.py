from odoo import models

# Confirmation popup before Validate on Delivery Order
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.env.context.get('skip_confirm'):
            return super().button_validate()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirmation',
            'res_model': 'confirm.validate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            }
        }