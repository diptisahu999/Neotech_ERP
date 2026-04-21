from odoo import models, fields

class QualityAssuranceControl(models.Model):
    _name = 'qa.control'
    _description = 'Quality Assurance Control'
    _order = 'id desc'

    name = fields.Char("Task", required=True)