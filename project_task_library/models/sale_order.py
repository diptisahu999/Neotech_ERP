from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_project(self):
        """Override to open existing project or create a new one"""
        self.ensure_one()
        
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
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'commitment_date': self.commitment_date,
            'salesperson_id': self.user_id.id,
            'amount_total': self.amount_total,
            'order_date': self.date_order,
        })
        self.project_id = project

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }