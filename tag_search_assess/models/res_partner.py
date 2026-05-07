from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    can_search_more_tags = fields.Boolean(
        compute='_compute_can_search_more_tags',
        string="Can Current User Search More Tags"
    )

    @api.depends_context('uid')
    def _compute_can_search_more_tags(self):
        can_search = self.env.user.can_search_more_tags
        for partner in self:
            partner.can_search_more_tags = can_search

