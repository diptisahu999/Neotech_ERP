from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectQALine(models.Model):
    _name = 'project.qa.line'
    _description = 'Project QA Line'

    project_id = fields.Many2one('project.project', ondelete='cascade')
    qa_id = fields.Many2one('qa.control', required=True)

    is_done = fields.Boolean("Done")
    done_by = fields.Many2one('res.users', string="Done By", readonly=True)
    done_date = fields.Datetime(string="Done Date", readonly=True)

    # 🔥 FIX: Persist values on save
    def write(self, vals):
        for rec in self:
            if 'is_done' in vals:
                if vals['is_done']:
                    vals.update({
                        'done_by': self.env.user.id,
                        'done_date': fields.Datetime.now(),
                    })
                else:
                    vals.update({
                        'done_by': False,
                        'done_date': False,
                    })
        return super().write(vals)