from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    person_name = fields.Char(string='Contact Name')
