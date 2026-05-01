from odoo import models, fields, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    opening_balance = fields.Float(
        string="Opening Balance",
        default=False,
        copy=False
    )

    opening_balance_type = fields.Selection([
        ('dr', 'Debit'),
        ('cr', 'Credit')
    ],
        string="Type",
        default=False,
        copy=False
    )

    opening_move_id = fields.Many2one(
        'account.move',
        readonly=True,
        copy=False
    )

    has_opening_entry = fields.Boolean(
        compute="_compute_has_entry",
        store=False
    )

    # -----------------------------------
    # COMPUTE
    # -----------------------------------

    def _compute_has_entry(self):
        for rec in self:
            rec.has_opening_entry = bool(rec.opening_move_id)

    # -----------------------------------
    # CREATE OPENING ENTRY
    # -----------------------------------

    def action_create_opening(self):
        self.ensure_one()

        if self.opening_move_id:
            raise UserError("Opening balance already exists.")

        # VALIDATE AMOUNT
        if not self.opening_balance:
            raise UserError("Enter opening balance.")

        if self.opening_balance < 1:
            raise UserError(
                "Opening balance must be greater than or equal to 1."
            )

        # VALIDATE TYPE
        if not self.opening_balance_type:
            raise UserError("Select Debit or Credit.")

        # JOURNAL
        journal = self.env['account.journal'].search(
            [('type', '=', 'general')],
            limit=1
        )

        if not journal:
            raise UserError(
                "Create Miscellaneous Journal first."
            )

        # PARTNER
        partner = self.commercial_partner_id

        # ACCOUNT
        account = (
            partner.property_account_receivable_id
            or partner.property_account_payable_id
        )

        if not account:
            raise UserError(
                "Configure Receivable/Payable Account."
            )

        # EQUITY ACCOUNT
        equity = self.env['account.account'].search([
            ('account_type', 'in', [
                'equity',
                'equity_unaffected'
            ])
        ], limit=1)

        if not equity:
            raise UserError("No Equity account found.")

        # AMOUNT
        debit = (
            self.opening_balance
            if self.opening_balance_type == 'dr'
            else 0
        )

        credit = (
            self.opening_balance
            if self.opening_balance_type == 'cr'
            else 0
        )

        # CREATE MOVE
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f'Opening Balance - {partner.name}',
            'line_ids': [

                # PARTNER LINE
                (0, 0, {
                    'account_id': account.id,
                    'partner_id': partner.id,
                    'debit': debit,
                    'credit': credit,
                    'name': 'Opening Balance',
                }),

                # EQUITY LINE
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

        # CHATTER LOG
        type_label = dict(
            self._fields[
                'opening_balance_type'
            ].selection
        ).get(self.opening_balance_type)

        self.message_post(
            body=(
                f"Opening Balance "
                f"{self.opening_balance} "
                f"{type_label} Saved"
            )
        )

    # -----------------------------------
    # DELETE OPENING ENTRY
    # -----------------------------------

    def action_delete_opening(self):
        self.ensure_one()

        if not self.opening_move_id:
            return

        # LOG BEFORE RESET
        type_label = dict(
            self._fields[
                'opening_balance_type'
            ].selection
        ).get(self.opening_balance_type)

        self.message_post(
            body=(
                f"Opening Balance "
                f"{self.opening_balance} "
                f"{type_label} Deleted"
            )
        )

        move = self.opening_move_id

        # DRAFT
        if move.state == 'posted':
            move.button_draft()

        # DELETE MOVE
        move.unlink()

        # RESET
        self.opening_move_id = False
        self.opening_balance = False
        self.opening_balance_type = False