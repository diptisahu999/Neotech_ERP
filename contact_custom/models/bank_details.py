from odoo import models, fields

# IFSC Master
class BankIFSC(models.Model):
    _name = 'bank.ifsc'
    _description = 'Bank IFSC'

    name = fields.Char("IFSC Code", required=True)


# Branch Master
class BankBranch(models.Model):
    _name = 'bank.branch'
    _description = 'Bank Branch'

    name = fields.Char("Branch Name", required=True)


# Extend Bank Account
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    ifsc_id = fields.Many2one(
        'bank.ifsc',
        string="IFSC Code"
    )

    branch_id = fields.Many2one(
        'bank.branch',
        string="Branch"
    )