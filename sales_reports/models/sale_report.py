import base64
from odoo import models, fields, api
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_additional_notes = fields.Boolean(
        compute='_compute_has_additional_notes',
        store=False
    )
    has_terms = fields.Boolean(compute='_compute_has_terms')

    # This method checks if the 'additional_notes' field contains any non-empty 
    # content after stripping HTML tags and whitespace.
    def _compute_has_additional_notes(self):
        for rec in self:
            content = rec.additional_notes or ''

            # Remove HTML tags
            clean_text = re.sub('<[^<]+?>', '', content)

            # Remove spaces/newlines
            clean_text = clean_text.strip()

            rec.has_additional_notes = bool(clean_text)

    # This method checks if the 'note' field contains any non-empty 
    # content after stripping HTML tags and whitespace.
    def _compute_has_terms(self):
        for rec in self:
            import re
            content = rec.note or ''
            clean = re.sub('<[^<]+?>', '', content).strip()
            rec.has_terms = bool(clean)



    cleaned_note_html = fields.Html(compute='_compute_cleaned_note_html', store=False)

    def _compute_cleaned_note_html(self):
        for rec in self:
            if rec.note:
                import re
                # Strip trailing <p><br></p>, <p>&nbsp;</p>, <br>, and whitespace
                clean_html = re.sub(r'(<p[^>]*>(<br\s*/?>|\s|&nbsp;)*</p>\s*|<br\s*/?>\s*)+$', '', rec.note)
                rec.cleaned_note_html = clean_html
            else:
                rec.cleaned_note_html = False

    # Send New Quotation Report by Email
    def action_quotation_send(self):
        self.ensure_one()

        template = self.env.ref('sale.email_template_edi_sale')
        report = self.env.ref('sales_reports.action_report_quotation_vashi_style')
        pdf, _ = report._render_qweb_pdf(
            report.report_name,
            res_ids=[self.id]
        )

        attachment = self.env['ir.attachment'].create({
            'name': f'Quotation-{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'res_model': 'mail.compose.message',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'sale.order',
                'default_res_ids': [self.id],
                'default_use_template': True,
                'default_template_id': template.id,

                # ✅ ONLY PDF ATTACHMENT, NO OTHER DEFAULTS
                'default_attachment_ids': [(6, 0, [attachment.id])],

                # 🔥 BLOCK Odoo default report completely
                'mark_so_as_sent': True,
            },
        }