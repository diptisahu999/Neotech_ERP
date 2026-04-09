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