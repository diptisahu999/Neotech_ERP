# pyrefly: ignore [missing-import]
from odoo import models, fields, api, _
import base64
import io
try:
    # pyrefly: ignore [missing-import]
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    # pyrefly: ignore [missing-import]
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter
    class PdfWriter(PdfFileWriter):
        def add_page(self, page):
            return self.addPage(page)


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

    @api.model_create_multi
    def create(self, vals_list):
        from datetime import datetime
        for vals in vals_list:
            if vals.get('name', 'New') == 'New' or vals.get('name') == '/':
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Date.context_today(self, fields.Datetime.to_datetime(vals['date_order']))
                raw_name = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or 'New'
                
                import re
                numbers = re.findall(r'\d+', raw_name)
                seq_num = numbers[-1] if numbers else '0001'
                
                order_date = fields.Datetime.to_datetime(vals.get('date_order')) if vals.get('date_order') else datetime.now()
                year = order_date.year
                if order_date.month >= 4:
                    fy_start = year
                    fy_end = year + 1
                else:
                    fy_start = year - 1
                    fy_end = year
                fy_str = f"{str(fy_start)[2:]}/{str(fy_end)[2:]}" # e.g. "26/27"
                
                vals['name'] = f"QT/{fy_str}/{seq_num}"
        return super(SaleOrder, self).create(vals_list)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    gst_percent = fields.Float(string='GST %', compute='_compute_gst_percent', store=True)

    @api.depends('tax_id')
    def _compute_gst_percent(self):
        for line in self:
            line.gst_percent = sum(line.tax_id.mapped('amount'))


    


    
# ==============================
# Report Merge Logic
# ==============================
# SO/Quotation --> Document Upload --> Merge PDF with New Custom Report
class ReportMerge(models.AbstractModel):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):

        # Define the list of reports that should support PDF merging
        allowed_reports = [
            'sales_reports.report_unified_quotation_new',
            'sales_reports.report_quotation_new_format_document',
            'sales_reports.report_unified_quotation',
            'sales_reports.report_unified_proforma'
        ]

        # Only apply for allowed reports
        if report_ref not in allowed_reports:
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