from odoo import models, fields, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    opening_balance = fields.Float(string="Opening Balance")
    opening_balance_type = fields.Selection([
        ('dr', 'Debit'),
        ('cr', 'Credit')
    ], string="Type")

    opening_move_id = fields.Many2one('account.move', readonly=True)

    has_opening_entry = fields.Boolean(
        compute="_compute_has_entry",
        store=False
    )

    def _compute_has_entry(self):
        for rec in self:
            rec.has_opening_entry = bool(rec.opening_move_id)

    # ✅ CREATE ENTRY
    def action_create_opening(self):
        self.ensure_one()

        if self.opening_move_id:
            raise UserError("Opening balance already exists.")

        if not self.opening_balance:
            raise UserError("Enter opening balance.")

        if not self.opening_balance_type:
            raise UserError("Select Debit or Credit.")

        journal = self.env['account.journal'].search(
            [('type', '=', 'general')], limit=1)

        if not journal:
            raise UserError("Create Miscellaneous Journal first.")

        # Account selection
        if self.customer_rank > 0:
            account = self.property_account_receivable_id
        elif self.supplier_rank > 0:
            account = self.property_account_payable_id
        else:
            raise UserError("Partner must be Customer or Vendor.")

        if not account:
            raise UserError("Missing receivable/payable account.")

        # Equity account
        equity = self.env['account.account'].search([
            ('account_type', 'in', ['equity', 'equity_unaffected'])
        ], limit=1)

        if not equity:
            raise UserError("No Equity account found.")

        debit = self.opening_balance if self.opening_balance_type == 'dr' else 0
        credit = self.opening_balance if self.opening_balance_type == 'cr' else 0

        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f'Opening Balance - {self.name}',
            'line_ids': [
                (0, 0, {
                    'account_id': account.id,
                    'partner_id': self.id,
                    'debit': debit,
                    'credit': credit,
                    'name': 'Opening Balance',
                }),
                (0, 0, {
                    'account_id': equity.id,
                    'debit': credit,
                    'credit': debit,
                    'name': 'Opening Balance Equity',
                }),
            ]
        })

        move.action_post()
        self.opening_move_id = move.id

    # ✅ DELETE ENTRY
    def action_delete_opening(self):
        self.ensure_one()

        if not self.opening_move_id:
            return

        move = self.opening_move_id

        if move.state == 'posted':
            move.button_draft()

        move.unlink()

        self.opening_move_id = False
        self.opening_balance = 0.0