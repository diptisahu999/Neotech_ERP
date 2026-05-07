from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    can_search_more_tags = fields.Boolean(
        string='Can Search More Tags',
        default=True,
        help="If unchecked, the user will not see the 'Search More...' option in tag fields."
    )


