from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()

        # ✅ If PO has project → pass to Vendor Bill
        if self.project_id:
            vals['project_id'] = self.project_id.id
        else:
            vals['project_id'] = False

        return vals