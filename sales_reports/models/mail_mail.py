from odoo import models, fields
import ast

class MailMail(models.Model):
    _inherit = 'mail.mail'

    x_user_id = fields.Many2one('res.users', string="Sender User")

    def send(self, auto_commit=False, raise_exception=False):
        MailServer = self.env['ir.mail_server']

        for mail in self:
            selected_server = False

            user = mail.x_user_id  # ✅ real user (not System)

            if user:
                for server in MailServer.search([]):
                    # 👇 match using NAME (your requirement)
                    if server.name == user.name:
                        selected_server = server
                        break

            if selected_server:
                mail.mail_server_id = selected_server.id
            else:
                servers = MailServer.search([])
                if servers:
                    mail.mail_server_id = servers[0].id

        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)
    

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail(auto_commit=auto_commit)

        for wizard in self:
            model = wizard.model
            res_ids = wizard.res_ids or []

            # ✅ FIX HERE
            if isinstance(res_ids, str):
                res_ids = ast.literal_eval(res_ids)

            if not model or not res_ids:
                continue

            mails = self.env['mail.mail'].sudo().search([
                ('model', '=', model),
                ('res_id', 'in', res_ids)
            ], order='id desc', limit=20)

            for mail in mails:
                mail.sudo().write({
                    'x_user_id': wizard.env.user.id
                })

        return res