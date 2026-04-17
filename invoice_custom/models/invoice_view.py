from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()

        # Case 1: If project exists in SO → pass to invoice
        if self.project_id:
            vals['project_id'] = self.project_id.id
        else:
            # Case 2: No project → keep empty (no need to assign)
            vals['project_id'] = False

        return vals
    

class AccountMove(models.Model):
    _inherit = 'account.move'

    project_id = fields.Many2one('project.project', string="Project")