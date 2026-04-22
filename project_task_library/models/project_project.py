from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_project_progress = fields.Float(
        string="Progress",
        compute="_compute_x_project_progress",
        help="Calculates progress based on top-level tasks and their sub-tasks completion."
    )

    # From Sale Order / Quotation
    x_sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one('res.partner', string="Customer", related='x_sale_order_id.partner_id', readonly=True, ondelete='cascade')
    salesperson_id = fields.Many2one('res.users', string="Salesperson", related='x_sale_order_id.user_id', readonly=True)
    amount_total = fields.Monetary(string="Order Value", related='x_sale_order_id.amount_total', readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='x_sale_order_id.currency_id', readonly=True)
    order_date = fields.Datetime(string="Order Date", related='x_sale_order_id.date_order', readonly=True)
    commitment_date = fields.Datetime(string="Delivery Date", related='x_sale_order_id.commitment_date', readonly=True)
    x_is_late = fields.Boolean(compute='_compute_x_is_late', string="Is Late")
    x_remaining_days = fields.Datetime(related='commitment_date', string="Due Day")
    x_is_today = fields.Boolean(compute='_compute_x_is_today')
    qa_line_ids = fields.One2many('project.qa.line', 'project_id', string="QA Control", ondelete='cascade')

    @api.depends('commitment_date')
    def _compute_x_is_today(self):
        today = fields.Date.context_today(self)
        for project in self:
            project.x_is_today = project.commitment_date and project.commitment_date.date() == today

    @api.depends('commitment_date', 'x_sale_order_id.delivery_status')
    def _compute_x_is_late(self):
        now = fields.Datetime.now()
        for project in self:
            is_late = False
            if project.commitment_date and project.commitment_date < now:
                # If there's a sale order, check its delivery status.
                # If no sale order, we just compare the date.
                if project.x_sale_order_id:
                    if project.x_sale_order_id.delivery_status != 'full':
                        is_late = True
                else:
                    is_late = True
            project.x_is_late = is_late


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


    # Override unlink to reset QA fields in related Sale Order
    def unlink(self):
        for project in self:
            # delete QA lines from project
            project.qa_line_ids.unlink()

        return super().unlink()