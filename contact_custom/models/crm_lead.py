from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    person_name = fields.Char(
        string='Contact Name', 
        related='partner_id.person_name', 
        readonly=False, 
        store=True
    )
