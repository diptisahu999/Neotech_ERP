from odoo import models, fields, api

class CrmTag(models.Model):
    _inherit = 'crm.tag'

    can_search_more_tags = fields.Boolean(
        compute='_compute_can_search_more_tags',
        string="Can Current User Search More Tags"
    )

    @api.depends_context('uid')
    def _compute_can_search_more_tags(self):
        can_search = self.env.user.can_search_more_tags
        for tag in self:
            tag.can_search_more_tags = can_search

    def action_delete_tag(self):
        self.ensure_one()
        if self.env.user.can_search_more_tags:
            return self.sudo().unlink()
        else:
            raise models.ValidationError("You do not have permission to delete tags.")

