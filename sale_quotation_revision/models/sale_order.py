from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('revision_number')
    def _compute_revision_number_display(self):
        for order in self:
            order.revision_number_display = str(order.revision_number).zfill(3)

    revision_number = fields.Integer(string='Revision', default=0, copy=False)
    active = fields.Boolean(string='Active', default=True, copy=False)
    revision_number_display = fields.Char(string='Revision Number', compute='_compute_revision_number_display', store=True)
    original_order_id = fields.Many2one('sale.order', string='Original Order', copy=False)
    revision_ids = fields.One2many('sale.order', 'original_order_id', string='Revisions')
    revision_count = fields.Integer(compute='_compute_revision_count', string='Revision Count')

    def write(self, vals):
        # List of fields to ignore for revision increment
        ignore_fields = [
            'message_main_attachment_id', 'access_token', 'access_url', 
            'access_warning', 'revision_number', 'revision_number_display', 
            'name', 'state', 'write_date', 'write_uid'
        ]
        
        # Only increment if a significant field is changed and it's in a state that allows revisions
        if any(f not in ignore_fields for f in vals):
            for order in self:
                # ONLY if the order is already saved (has an ID) and in a relevant state
                if isinstance(order.id, (int, models.NewId)) and not isinstance(order.id, models.NewId) and order.state in ['draft', 'sent', 'sale']:
                    new_rev = order.revision_number + 1
                    vals['revision_number'] = new_rev
                    
                    # Identify which fields triggered the revision and get old/new values
                    details = []
                    for field, new_val in vals.items():
                        if field in order._fields and field not in ignore_fields:
                            f_obj = order._fields[field]
                            old_val = order[field]
                            
                            # Helper to format values nicely (e.g. Many2one names)
                            def format_v(val, field_obj):
                                if field_obj.type in ['one2many', 'many2many']:
                                    return _("(Data Updated)")
                                if not val: return "None"
                                if field_obj.type == 'many2one':
                                    if isinstance(val, models.BaseModel):
                                        return val.display_name or "None"
                                    return order.env[field_obj.comodel_name].browse(val).display_name or "None"
                                return str(val)

                            if f_obj.type in ['one2many', 'many2many']:
                                # Handle relational fields (Order Lines)
                                if field == 'order_line':
                                    for cmd in new_val:
                                        if cmd[0] == 1: # Update
                                            line = order.order_line.filtered(lambda l: l.id == cmd[1])
                                            line_vals = cmd[2]
                                            for l_f, l_nv in line_vals.items():
                                                if l_f in line._fields:
                                                    l_obj = line._fields[l_f]
                                                    l_ov = line[l_f]
                                                    
                                                    # def fmt(v, obj):
                                                    #     if obj.type == 'many2one': return order.env[obj.comodel_name].browse(v).display_name or "None"
                                                    #     return str(v)
                                                    def fmt(v, obj):
                                                        if obj.type == 'many2one':

                                                            # Empty value
                                                            if not v:
                                                                return "None"

                                                            # Already a recordset
                                                            if hasattr(v, '_name'):
                                                                return v.display_name or "None"

                                                            # Tuple/list format
                                                            if isinstance(v, (list, tuple)):
                                                                v = v[0] if v else False

                                                            # Integer ID
                                                            if isinstance(v, int):
                                                                rec = order.env[obj.comodel_name].browse(v)
                                                                return rec.display_name or "None"

                                                            return str(v)
                                                    
                                                    ov_s, nv_s = fmt(l_ov, l_obj), fmt(l_nv, l_obj)
                                                    if ov_s != nv_s:
                                                        details.append(f" {l_obj.string} ({line.product_id.name}): {ov_s} → {nv_s}")
                                        elif cmd[0] == 0: # New line
                                            details.append(f" {f_obj.string} : New line added")
                                        elif cmd[0] == 2: # Delete line
                                            details.append(f" {f_obj.string} : Line removed")
                                else:
                                    details.append(f" {f_obj.string} : (Data Updated)")
                            else:
                                old_str = format_v(old_val, f_obj)
                                new_str = format_v(new_val, f_obj)
                                if old_str != new_str:
                                    details.append(f" {f_obj.string} : {old_str} → {new_str}")
                    
                    if details:
                        # CREATE A SNAPSHOT ARCHIVE of the old version
                        root_order = order.original_order_id or order
                        snapshot_vals = {
                            'name': f"{order.name}-R{order.revision_number_display}",
                            'original_order_id': root_order.id,
                            'state': 'cancel',
                            'active': False,
                            'revision_number': order.revision_number,
                        }
                        order.with_context(no_revision=True, mail_auto_subscribe_no_notify=True).copy(snapshot_vals)

                        msg = _(" Revision %s :: triggered by: %s") % (str(new_rev).zfill(3), " : ".join(details))
                        order.message_post(body=msg)
                    break # Single record update logic
        
        return super(SaleOrder, self).write(vals)

    @api.depends('original_order_id', 'revision_ids', 'original_order_id.revision_ids')
    def _compute_revision_count(self):
        for order in self:
            root_order = order.original_order_id or order
            # Count only the archived snapshots
            order.revision_count = self.with_context(active_test=False).search_count([
                ('original_order_id', '=', root_order.id)
            ])

    def action_view_revisions(self):
        self.ensure_one()
        root_order = self.original_order_id or self
        # Domain includes the root order and all its revisions
        domain = ['|', ('id', '=', root_order.id), ('original_order_id', '=', root_order.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Revisions'),
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': domain,
            'context': dict(self.env.context, create=False, active_test=False),
        }
