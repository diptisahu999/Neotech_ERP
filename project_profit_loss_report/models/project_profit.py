from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    revenue = fields.Float(compute="_compute_profit")
    material_cost = fields.Float(compute="_compute_profit")
    purchase_cost = fields.Float(compute="_compute_profit")
    total_cost = fields.Float(compute="_compute_profit")
    profit = fields.Float(compute="_compute_profit")

    @api.depends_context()
    def _compute_profit(self):
        AccountMove = self.env['account.move']
        Valuation = self.env['stock.valuation.layer']

        for rec in self:
            # Revenue
            invoices = AccountMove.search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('project_id', '=', rec.id)
            ])
            rec.revenue = sum(invoices.mapped('amount_total'))

            # Material Cost (FIXED)
            valuation_layers = Valuation.search([
                ('stock_move_id.raw_material_production_id.project_id', '=', rec.id)
            ])
            rec.material_cost = abs(sum(valuation_layers.mapped('value')))

            # Purchase Cost
            bills = AccountMove.search([
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('project_id', '=', rec.id),
            ])
            rec.purchase_cost = sum(bills.mapped('amount_total'))

            # Totals
            rec.total_cost = rec.purchase_cost
            rec.profit = rec.revenue - rec.total_cost