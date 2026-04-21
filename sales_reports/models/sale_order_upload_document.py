from odoo import models, fields
import base64
import io
from PyPDF2 import PdfReader, PdfWriter

# SO/Quotation --> Document Upload
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    document_file = fields.Binary("Upload Document")
    document_filename = fields.Char("File Name")

    document_position = fields.Selection([
        ('header', 'Header'),
        ('footer', 'Footer')
    ], string="Document Position")

    def action_remove_document(self):
        for rec in self:
            rec.document_file = False
            rec.document_filename = False
            rec.document_position = False

# SO/Quotation --> Document Upload --> Merge PDF with New Custom Report
class ReportMerge(models.AbstractModel):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):

        if report_ref != 'sales_reports.report_unified_quotation_new':
            return super()._render_qweb_pdf(report_ref, res_ids, data)

        records = self.env['sale.order'].browse(res_ids)
        final_writer = PdfWriter()

        for record in records:

            # Generate base PDF per record
            pdf_content, content_type = super()._render_qweb_pdf(
                report_ref, res_ids=[record.id], data=data
            )

            base_pdf = PdfReader(io.BytesIO(pdf_content))

            if not record.document_file:
                for page in base_pdf.pages:
                    final_writer.add_page(page)
                continue

            attachment_pdf = PdfReader(
                io.BytesIO(base64.b64decode(record.document_file))
            )

            if record.document_position == 'header':
                for page in attachment_pdf.pages:
                    final_writer.add_page(page)
                for page in base_pdf.pages:
                    final_writer.add_page(page)

            elif record.document_position == 'footer':
                for page in base_pdf.pages:
                    final_writer.add_page(page)
                for page in attachment_pdf.pages:
                    final_writer.add_page(page)

            else:
                for page in base_pdf.pages:
                    final_writer.add_page(page)

        output = io.BytesIO()
        final_writer.write(output)

        return output.getvalue(), 'pdf'