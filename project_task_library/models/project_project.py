from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_project_progress = fields.Float(
        string="Progress",
        compute="_compute_x_project_progress",
        help="Calculates progress based on top-level tasks and their sub-tasks completion."
    )

    # From Sale Order / Quotation
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one('res.partner', string="Customer")
    salesperson_id = fields.Many2one('res.users', string="Salesperson", store=True, readonly=True)
    amount_total = fields.Monetary(string="Order Value", store=True, readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', store=True, readonly=True)
    order_date = fields.Datetime(string="Order Date", store=True, readonly=True)
    commitment_date = fields.Datetime(string="Delivery Date", store=True, readonly=True)


    @api.depends('tasks.is_closed', 'tasks.subtask_completion_percentage', 'tasks.parent_id')
    def _compute_x_project_progress(self):
        for project in self:
            # We only care about top-level tasks (those with no parent)
            top_level_tasks = project.tasks.filtered(lambda t: not t.parent_id)
            if not top_level_tasks:
                project.x_project_progress = 0.0
                continue
            
            total_progress = 0.0
            for task in top_level_tasks:
                if task.child_ids:
                    # If it has sub-tasks, use the sub-task completion percentage
                    total_progress += task.subtask_completion_percentage
                else:
                    # If no sub-tasks, it's either 100% (closed) or 0% (open)
                    total_progress += 1.0 if task.is_closed else 0.0
            
            # Average the progress of all top-level tasks and convert to percentage (0-100)
            project.x_project_progress = (total_progress / len(top_level_tasks)) * 100