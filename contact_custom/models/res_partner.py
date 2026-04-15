from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    person_name = fields.Char(string='Contact Name')
    created_by_id = fields.Many2one(
        'res.users',
        string='Created By',
        related='create_uid',
        readonly=True,
        store=True,
    )
