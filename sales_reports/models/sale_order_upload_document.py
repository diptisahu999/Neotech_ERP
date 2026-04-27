from odoo import models, fields
import base64
import io
from PyPDF2 import PdfReader, PdfWriter

# SO/Quotation --> Document Upload
# ==============================
# Sale Order Extension
# ==============================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    header_file = fields.Binary("Header Document")
    header_filename = fields.Char("Header File Name")

    footer_file = fields.Binary("Footer Document")
    footer_filename = fields.Char("Footer File Name")

    def action_remove_header(self):
        self.header_file = False
        self.header_filename = False

    def action_remove_footer(self):
        self.footer_file = False
        self.footer_filename = False

    


    
# ==============================
# Report Merge Logic
# ==============================
# SO/Quotation --> Document Upload --> Merge PDF with New Custom Report
class ReportMerge(models.AbstractModel):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):

        # Only apply for your custom report
        if report_ref != 'sales_reports.report_unified_quotation_new':
            return super()._render_qweb_pdf(report_ref, res_ids, data)

        records = self.env['sale.order'].browse(res_ids)
        final_writer = PdfWriter()

        for record in records:

            # Generate original report PDF
            pdf_content, _ = super()._render_qweb_pdf(
                report_ref, res_ids=[record.id], data=data
            )
            base_pdf = PdfReader(io.BytesIO(pdf_content))

            # ======================
            # HEADER (if exists)
            # ======================
            if record.header_file:
                try:
                    header_pdf = PdfReader(
                        io.BytesIO(base64.b64decode(record.header_file))
                    )
                    for page in header_pdf.pages:
                        final_writer.add_page(page)
                except Exception:
                    pass  # avoid crash if invalid PDF

            # ======================
            # MAIN REPORT
            # ======================
            for page in base_pdf.pages:
                final_writer.add_page(page)

            # ======================
            # FOOTER (if exists)
            # ======================
            if record.footer_file:
                try:
                    footer_pdf = PdfReader(
                        io.BytesIO(base64.b64decode(record.footer_file))
                    )
                    for page in footer_pdf.pages:
                        final_writer.add_page(page)
                except Exception:
                    pass  # avoid crash if invalid PDF

        # ======================
        # FINAL OUTPUT
        # ======================
        output = io.BytesIO()
        final_writer.write(output)

        return output.getvalue(), 'pdf'