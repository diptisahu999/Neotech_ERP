from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmLeadDistributeWizard(models.TransientModel):
    _name = 'crm.lead.distribute.wizard'
    _description = 'Distribute Lead to Salespersons'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead / Inquiry',
        required=True,
        readonly=True,
    )
    lead_name = fields.Char(
        related='lead_id.name',
        string='Lead Name',
        readonly=True,
    )
    salesperson_ids = fields.Many2many(
        'res.users',
        'crm_lead_dist_wizard_user_rel',
        'wizard_id',
        'user_id',
        string='Salespersons',
        domain=[('share', '=', False), ('active', '=', True)],
    )
    note = fields.Text(
        string='Internal Note',
        help='Optional note added to each distributed lead copy.',
    )

    @api.constrains('salesperson_ids')
    def _check_salesperson_count(self):
        for wizard in self:
            count = len(wizard.salesperson_ids)
            if count > 0 and (count < 3 or count > 5):
                raise ValidationError(
                    f'Select between 3 and 5 salespersons. Currently selected: {count}.'
                )

    def action_distribute(self):
        self.ensure_one()
        count = len(self.salesperson_ids)
        if count < 3 or count > 5:
            raise ValidationError(
                f'Select between 3 and 5 salespersons. Currently selected: {count}.'
            )

        lead = self.lead_id

        # Find the first stage (lowest sequence)
        first_stage = self.env['crm.stage'].search(
            [], order='sequence asc', limit=1
        )

        for salesperson in self.salesperson_ids:
            new_lead = lead.copy({
                'user_id': salesperson.id,
                'stage_id': first_stage.id if first_stage else lead.stage_id.id,
            })
            if self.note:
                new_lead.message_post(
                    body=f'<b>Distribution Note:</b><br/>{self.note}',
                    subtype_xmlid='mail.mt_note',
                )

        # Tag the original lead as Distributed
        tag = self.env['crm.tag'].search([('name', '=', 'Distributed')], limit=1)
        if not tag:
            tag = self.env['crm.tag'].create({'name': 'Distributed'})
        lead.write({'tag_ids': [(4, tag.id)]})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Lead Distributed',
                'message': f'"{lead.name}" distributed to {count} salesperson(s).',
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
