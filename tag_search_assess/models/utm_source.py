from odoo import models, fields, api

class UtmSource(models.Model):
    _inherit = 'utm.source'

    can_search_more_tags = fields.Boolean(
        compute='_compute_can_search_more_tags',
        string="Can Current User Search More"
    )

    @api.depends_context('uid')
    def _compute_can_search_more_tags(self):
        can_search = self.env.user.can_search_more_tags
        for source in self:
            source.can_search_more_tags = can_search

    def action_delete_source(self):
        self.ensure_one()
        if self.env.user.can_search_more_tags:
            return self.sudo().unlink()
        else:
            raise models.ValidationError("You do not have permission to delete sources.")
