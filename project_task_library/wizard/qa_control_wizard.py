from odoo import models, fields

class QaControlWizard(models.TransientModel):
    _name = 'qa.control.wizard'

    sale_id = fields.Many2one('sale.order')
    qa_task_ids = fields.Many2many('qa.control', string="QA Tasks")

    def action_done(self):
        self.ensure_one()

        self.sale_id.qa_task_ids = [(6, 0, self.qa_task_ids.ids)]
        self.sale_id.qa_assigned = True

        return self.sale_id._create_project_internal()

    def action_cancel(self):
        # 👇 IMPORTANT: Still create project
        return self.sale_id._create_project_internal()