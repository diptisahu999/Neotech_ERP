# pyrefly: ignore [missing-import]
from odoo import models, fields, api, _
# pyrefly: ignore [missing-import]
from odoo.exceptions import UserError
import re
import ast
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('revision_number')
    def _compute_revision_number_display(self):
        for order in self:
            order.revision_number_display = f"R{order.revision_number}"

    revision_number = fields.Integer(string='Revision', default=0, copy=False)
    active = fields.Boolean(string='Active', default=True, copy=False)
    revision_number_display = fields.Char(string='Revision Number', compute='_compute_revision_number_display', store=True)
    original_order_id = fields.Many2one('sale.order', string='Original Order', copy=False)
    revision_ids = fields.One2many('sale.order', 'original_order_id', string='Revisions')
    revision_count = fields.Integer(compute='_compute_revision_count', string='Revision Count')
    show_submit_button = fields.Boolean(string='Show Submit Button', default=False, copy=False)
    revision_change_log = fields.Text(string='Revision Change Log', copy=False)
    pending_revision_id = fields.Many2one('sale.order', string='Pending Revision Snapshot', copy=False)

    @api.model
    def action_fix_snapshot_names(self):
        # Fix snapshot names
        snapshots = self.with_context(active_test=False).search([('name', 'like', '%-00%')])
        for snap in snapshots:
            if '-' in snap.name:
                base, suffix = snap.name.rsplit('-', 1)
                if suffix.isdigit():
                    snap.name = f"{base}-R{int(suffix)}"
        
        # Fix stored revision_number_display
        orders = self.with_context(active_test=False).search([('revision_number_display', 'like', '00%')])
        for order in orders:
            order.revision_number_display = f"R{order.revision_number}"

    # This method hide / show 'Submit' Button
    # This Button used for Submit Revision (Create New Revision)
    def write(self, vals):
        for order in self:

            # Hide button once confirmed
            if vals.get('state') == 'sale':
                vals['show_submit_button'] = False

            # Show button if quotation updated
            elif order.state in ['draft', 'sent']:
                ignore_fields = [
                    'write_date',
                    'write_uid',
                    'show_submit_button',
                    'revision_change_log',
                    'revision_number',
                    'revision_number_display',
                    'name',
                    'state',
                    'active',
                    'message_main_attachment_id',
                    'access_token',
                    'access_url',
                    'access_warning',
                    'terms_section',
                    'remarks_section',
                    'note',
                    'pending_revision_id',
                ]

                _logger.info("REVISION WRITE tracking check on order %s (show_submit_button=%s): vals = %s", order.name, order.show_submit_button, vals)
                if any(field not in ignore_fields for field in vals):
                    # Create the snapshot BEFORE writing the new values to database
                    if not order.show_submit_button:
                        root_order = order.original_order_id or order
                        snapshot_vals = {
                            'name': f"{order.name}-{order.revision_number_display}",
                            'original_order_id': False,
                            'state': 'cancel',
                            'active': False,
                            'revision_number': order.revision_number,
                        }
                        snapshot = order.with_context(
                            no_revision=True,
                            mail_auto_subscribe_no_notify=True
                        ).copy(snapshot_vals)
                        super(SaleOrder, order).write({'pending_revision_id': snapshot.id})

                    # Capture old/original values before they are modified in this write
                    old_vals = {}
                    if order.show_submit_button and order.revision_change_log:
                        try:
                            old_vals = ast.literal_eval(order.revision_change_log)
                        except Exception:
                            old_vals = {}

                    def serialize_val(val, field_obj):
                        if not val:
                            return False
                        if field_obj.type == 'many2one':
                            return val.id
                        if field_obj.type in ['date', 'datetime']:
                            return str(val)
                        if field_obj.type in ['one2many', 'many2many']:
                            return "(Data Updated)"
                        if isinstance(val, (int, float, bool)):
                            return val
                        return str(val)

                    for field, new_val in vals.items():
                        _logger.info("REVISION WRITE loop: field = %s, new_val = %s", field, new_val)
                        if field in ignore_fields or field not in order._fields:
                            continue
                        
                        f_obj = order._fields[field]
                        if f_obj.type == 'binary':
                            continue
                        
                        if f_obj.type in ['one2many', 'many2many']:
                            if field == 'order_line':
                                if 'order_line' not in old_vals:
                                    old_vals['order_line'] = []
                                
                                for cmd in new_val:
                                    if cmd[0] == 1: # Update existing line
                                        line_id = cmd[1]
                                        line_vals = cmd[2]
                                        line = order.order_line.filtered(lambda l: l.id == line_id)
                                        if line:
                                            existing_cmd = None
                                            for ex in old_vals['order_line']:
                                                if ex[0] == 1 and ex[1] == line_id:
                                                    existing_cmd = ex
                                                    break
                                            
                                            if existing_cmd:
                                                # Add untracked fields' original values
                                                for lf, lnv in line_vals.items():
                                                    if lf in line._fields and lf not in existing_cmd[2]:
                                                        existing_cmd[2][lf] = serialize_val(line[lf], line._fields[lf])
                                            else:
                                                orig_line_vals = {}
                                                for lf, lnv in line_vals.items():
                                                    if lf in line._fields:
                                                        orig_line_vals[lf] = serialize_val(line[lf], line._fields[lf])
                                                old_vals['order_line'].append((1, line_id, orig_line_vals))
                                    
                                    elif cmd[0] == 0: # New line
                                        old_vals['order_line'].append((0, 0, {}))
                                    
                                    elif cmd[0] == 2: # Delete line
                                        old_vals['order_line'].append((2, cmd[1], 0))
                        else:
                            if field not in old_vals:
                                old_vals[field] = serialize_val(order[field], f_obj)
                                _logger.info("REVISION WRITE captured standard: field = %s, old_val = %s", field, old_vals[field])

                    vals['show_submit_button'] = True
                    vals['revision_change_log'] = str(old_vals)
                    _logger.info("REVISION WRITE finalized: revision_change_log = %s", vals['revision_change_log'])

        return super(SaleOrder, self).write(vals)

    # def write(self, vals):
    #     # List of fields to ignore for revision increment
    #     ignore_fields = [
    #         'message_main_attachment_id', 'access_token', 'access_url', 
    #         'access_warning', 'revision_number', 'revision_number_display', 
    #         'name', 'state', 'write_date', 'write_uid'
    #     ]
        
    #     # Only increment if a significant field is changed and it's in a state that allows revisions
    #     if any(f not in ignore_fields for f in vals):
    #         for order in self:
    #             # ONLY if the order is already saved (has an ID) and in a relevant state
    #             if isinstance(order.id, (int, models.NewId)) and not isinstance(order.id, models.NewId) and order.state in ['draft', 'sent', 'sale']:
    #                 new_rev = order.revision_number + 1
    #                 vals['revision_number'] = new_rev
                    
    #                 # Identify which fields triggered the revision and get old/new values
    #                 details = []
    #                 for field, new_val in vals.items():
    #                     if field in order._fields and field not in ignore_fields:
    #                         f_obj = order._fields[field]
    #                         old_val = order[field]
                            
    #                         # Helper to format values nicely (e.g. Many2one names)
    #                         def format_v(val, field_obj):
    #                             if field_obj.type in ['one2many', 'many2many']:
    #                                 return _("(Data Updated)")
    #                             if not val: return "None"
    #                             if field_obj.type == 'many2one':
    #                                 if isinstance(val, models.BaseModel):
    #                                     return val.display_name or "None"
    #                                 return order.env[field_obj.comodel_name].browse(val).display_name or "None"
    #                             return str(val)

    #                         if f_obj.type in ['one2many', 'many2many']:
    #                             # Handle relational fields (Order Lines)
    #                             if field == 'order_line':
    #                                 for cmd in new_val:
    #                                     if cmd[0] == 1: # Update
    #                                         line = order.order_line.filtered(lambda l: l.id == cmd[1])
    #                                         line_vals = cmd[2]
    #                                         for l_f, l_nv in line_vals.items():
    #                                             if l_f in line._fields:
    #                                                 l_obj = line._fields[l_f]
    #                                                 l_ov = line[l_f]
                                                    
    #                                                 # def fmt(v, obj):
    #                                                 #     if obj.type == 'many2one': return order.env[obj.comodel_name].browse(v).display_name or "None"
    #                                                 #     return str(v)
    #                                                 def fmt(v, obj):
    #                                                     if obj.type == 'many2one':

    #                                                         # Empty value
    #                                                         if not v:
    #                                                             return "None"

    #                                                         # Already a recordset
    #                                                         if hasattr(v, '_name'):
    #                                                             return v.display_name or "None"

    #                                                         # Tuple/list format
    #                                                         if isinstance(v, (list, tuple)):
    #                                                             v = v[0] if v else False

    #                                                         # Integer ID
    #                                                         if isinstance(v, int):
    #                                                             rec = order.env[obj.comodel_name].browse(v)
    #                                                             return rec.display_name or "None"

    #                                                         return str(v)
                                                    
    #                                                 ov_s, nv_s = fmt(l_ov, l_obj), fmt(l_nv, l_obj)
    #                                                 if ov_s != nv_s:
    #                                                     details.append(f" {l_obj.string} ({line.product_id.name}): {ov_s} → {nv_s}")
    #                                     elif cmd[0] == 0: # New line
    #                                         details.append(f" {f_obj.string} : New line added")
    #                                     elif cmd[0] == 2: # Delete line
    #                                         details.append(f" {f_obj.string} : Line removed")
    #                             else:
    #                                 details.append(f" {f_obj.string} : (Data Updated)")
    #                         else:
    #                             old_str = format_v(old_val, f_obj)
    #                             new_str = format_v(new_val, f_obj)
    #                             if old_str != new_str:
    #                                 details.append(f" {f_obj.string} : {old_str} → {new_str}")
                    
    #                 if details:
    #                     # CREATE A SNAPSHOT ARCHIVE of the old version
    #                     root_order = order.original_order_id or order
    #                     snapshot_vals = {
    #                         'name': f"{order.name}-{order.revision_number_display}",
    #                         'original_order_id': root_order.id,
    #                         'state': 'cancel',
    #                         'active': False,
    #                         'revision_number': order.revision_number,
    #                     }
    #                     order.with_context(no_revision=True, mail_auto_subscribe_no_notify=True).copy(snapshot_vals)

    #                     msg = _(" Revision %s :: triggered by: %s") % (order.revision_number_display, " : ".join(details))
    #                     order.message_post(body=msg)
    #                 break # Single record update logic
        
    #     return super(SaleOrder, self).write(vals)

    @api.depends('original_order_id', 'revision_ids', 'original_order_id.revision_ids')
    def _compute_revision_count(self):
        for order in self:
            root_order = order.original_order_id or order
            # Count only the archived snapshots
            order.revision_count = self.with_context(active_test=False).search_count([
                ('original_order_id', '=', root_order.id)
            ])

    # This action for show Revisions smart button
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
    
    # This action for Submit Revision Button
    def action_submit_revision(self):
        # List of fields to ignore for revision log
        ignore_fields = [
            'message_main_attachment_id',
            'access_token',
            'access_url',
            'access_warning',
            'revision_number',
            'revision_number_display',
            'name',
            'state',
            'write_date',
            'write_uid',
            'show_submit_button',
            'terms_section',
            'remarks_section',
            'note',
        ]

        for order in self:
            # Only allow quotation stages
            if order.state not in ['draft', 'sent']:
                continue

            # Get changed values from context
            # vals = order.env.context.get('revision_vals', {})
            vals = {}
            if order.revision_change_log:
                try:
                    vals = ast.literal_eval(order.revision_change_log)
                except Exception:
                    vals = {}

            # New Revision Number
            new_rev = order.revision_number + 1

            # Identify changed fields
            details = []

            for field, new_val in vals.items():
                if field in order._fields and field not in ignore_fields:
                    f_obj = order._fields[field]
                    if f_obj.type == 'binary':
                        continue
                    old_val = order[field]

                    # Format values
                    def format_v(val, field_obj):
                        if field_obj.type in ['one2many', 'many2many']:
                            return _("(Data Updated)")

                        if not val:
                            return "None"

                        if field_obj.type == 'many2one':
                            if isinstance(val, models.BaseModel):
                                return val.display_name or "None"

                            return order.env[
                                field_obj.comodel_name
                            ].browse(val).display_name or "None"

                        if field_obj.type == 'html':
                            clean_val = re.sub('<[^<]+?>', '', str(val)).strip()
                            return clean_val or "None"

                        return str(val)

                    # Handle Order Lines
                    if f_obj.type in ['one2many', 'many2many']:
                        if field == 'order_line':
                            for cmd in new_val:
                                # Update Existing Line
                                if cmd[0] == 1:
                                    line = order.order_line.filtered(
                                        lambda l: l.id == cmd[1]
                                    )
                                    line_vals = cmd[2]
                                    for l_f, l_nv in line_vals.items():
                                        if l_f in line._fields:
                                            l_obj = line._fields[l_f]
                                            l_ov = line[l_f]

                                            def fmt(v, obj):
                                                if obj.type == 'many2one':
                                                    if not v:
                                                        return "None"

                                                    if hasattr(v, '_name'):
                                                        return v.display_name or "None"

                                                    if isinstance(v, (list, tuple)):
                                                        v = v[0] if v else False

                                                    if isinstance(v, int):
                                                        rec = order.env[
                                                            obj.comodel_name
                                                        ].browse(v)

                                                        return rec.display_name or "None"

                                                return str(v)

                                            ov_s = fmt(l_ov, l_obj)
                                            nv_s = fmt(l_nv, l_obj)

                                            if ov_s != nv_s:
                                                details.append(
                                                    f" {l_obj.string} "
                                                    f"({line.product_id.name})"
                                                    f": {nv_s} → {ov_s}"
                                                )
                                # New Line
                                elif cmd[0] == 0:
                                    details.append(
                                        f" {f_obj.string} : New line added"
                                    )
                                # Delete Line
                                elif cmd[0] == 2:
                                    details.append(
                                        f" {f_obj.string} : Line removed"
                                    )
                        else:
                            details.append(
                                f" {f_obj.string} : (Data Updated)"
                            )
                    else:
                        old_str = format_v(new_val, f_obj)
                        new_str = format_v(old_val, f_obj)

                        if old_str != new_str:
                            details.append(
                                f" {f_obj.string} : "
                                f"{old_str} → {new_str}"
                            )
            # Capture current revision display name before updating
            rev_disp = order.revision_number_display

            # Link the pending revision snapshot to the current order
            if order.pending_revision_id:
                root_order = order.original_order_id or order
                order.pending_revision_id.write({
                    'original_order_id': root_order.id,
                })

            # Update Current Order
            order.write({
                'revision_number': new_rev,
                'show_submit_button': False,
                'revision_change_log': False,
                'pending_revision_id': False,
            })

            # Chatter Log
            if details:
                msg = _(
                    " Revision %s :: triggered by: %s"
                ) % (
                    rev_disp,
                    " : ".join(details)
                )
            else:
                msg = _(
                    " Revision %s Submitted"
                ) % (
                    rev_disp
                )

            order.message_post(body=msg)
        return True
