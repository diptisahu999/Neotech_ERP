from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    neotech_crm_role = fields.Selection(
        selection=[
            ('salesperson', 'CRM Salesperson'),
            ('manager', 'CRM Manager'),
            ('none', 'No CRM Role'),
        ],
        string='CRM Role',
        compute='_compute_neotech_crm_role',
        store=False,
    )

    @api.depends('groups_id')
    def _compute_neotech_crm_role(self):
        try:
            sp_group = self.env.ref('crm_leads_menu.group_neotech_crm_salesperson')
            mgr_group = self.env.ref('crm_leads_menu.group_neotech_crm_manager')
        except Exception:
            for user in self:
                user.neotech_crm_role = 'none'
            return

        for user in self:
            if mgr_group in user.groups_id:
                user.neotech_crm_role = 'manager'
            elif sp_group in user.groups_id:
                user.neotech_crm_role = 'salesperson'
            else:
                user.neotech_crm_role = 'none'

    def action_set_crm_salesperson(self):
        sp_group  = self.env.ref('crm_leads_menu.group_neotech_crm_salesperson')
        mgr_group = self.env.ref('crm_leads_menu.group_neotech_crm_manager')
        # Odoo built-in Sales groups — must be "Own Docs Only" to enforce isolation
        own_docs  = self.env.ref('sales_team.group_sale_salesman')
        all_docs  = self.env.ref('sales_team.group_sale_salesman_all_leads')
        sale_mgr  = self.env.ref('sales_team.group_sale_manager')
        for user in self:
            user.write({
                'groups_id': [
                    (4, sp_group.id),   # Add: CRM Salesperson (own records)
                    (3, mgr_group.id),  # Remove: CRM Manager
                    (4, own_docs.id),   # Add: Sales → Own Documents Only
                    (3, all_docs.id),   # Remove: Sales → All Documents
                    (3, sale_mgr.id),   # Remove: Sales Manager
                ],
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Role Assigned',
                'message': f'{self[0].name} is now a CRM Salesperson (sees own records only).',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_set_crm_manager(self):
        sp_group  = self.env.ref('crm_leads_menu.group_neotech_crm_salesperson')
        mgr_group = self.env.ref('crm_leads_menu.group_neotech_crm_manager')
        # Managers get "All Documents" access
        all_docs  = self.env.ref('sales_team.group_sale_salesman_all_leads')
        own_docs  = self.env.ref('sales_team.group_sale_salesman')
        for user in self:
            user.write({
                'groups_id': [
                    (4, mgr_group.id),  # Add: CRM Manager
                    (3, sp_group.id),   # Remove: CRM Salesperson
                    (4, all_docs.id),   # Add: Sales → All Documents
                    (3, own_docs.id),   # Remove: Sales → Own Documents Only
                ],
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Role Assigned',
                'message': f'{self[0].name} is now a CRM Manager (sees all records).',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_remove_crm_role(self):
        sp_group  = self.env.ref('crm_leads_menu.group_neotech_crm_salesperson')
        mgr_group = self.env.ref('crm_leads_menu.group_neotech_crm_manager')
        for user in self:
            user.write({
                'groups_id': [(3, sp_group.id), (3, mgr_group.id)],
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Role Removed',
                'message': f'{self[0].name} CRM role has been removed.',
                'type': 'warning',
                'sticky': False,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('tz') == 'Asia/Calcutta':
                vals['tz'] = 'Asia/Kolkata'
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('tz') == 'Asia/Calcutta':
            vals['tz'] = 'Asia/Kolkata'
        return super().write(vals)

