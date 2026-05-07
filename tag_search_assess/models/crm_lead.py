from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    can_search_more_tags = fields.Boolean(
        compute='_compute_can_search_more_tags',
        string="Can Current User Search More Tags"
    )

    @api.depends_context('uid')
    def _compute_can_search_more_tags(self):
        can_search = self.env.user.can_search_more_tags
        for lead in self:
            lead.can_search_more_tags = can_search

