from odoo import models, api, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # This field Track in SO. ---------
    delivery_done = fields.Boolean(compute='_compute_delivery_done', string="Delivery Done")

    def _compute_delivery_done(self):
        for order in self:
            order.delivery_done = any(
                picking.state == 'done'
                for picking in order.picking_ids
            )
    # --------------------------------------

    def action_create_project(self):
        """Override to open existing project or create a new one"""
        self.ensure_one()

        # ❌ BLOCK: If delivery already validated
        if any(picking.state == 'done' for picking in self.picking_ids):
            raise UserError(_(
                "You cannot create a project after the delivery has been validated."
            ))

        # ✅ NEW CHECK: Order lines must exist
        valid_lines = self.order_line.filtered(lambda l: not l.display_type)
        if not valid_lines:
            raise UserError(_("First add product in list before creating project."))
        
        if self.state not in ['draft', 'sent', 'sale']:
            raise UserError(_("The Sales Order must be in a valid state (Draft, Sent, or Confirmed) to create a project."))
        
        # If already linked, just open the existing project
        if self.project_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.project_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Otherwise, create a new project
        project = self.env['project.project'].create({
            'name': f"{self.name} - {self.partner_id.name}",
            'x_sale_order_id': self.id,
        })
        self.project_id = project

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }