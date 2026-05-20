from odoo import models
import logging

_logger = logging.getLogger(__name__)


class NotificationManager(models.AbstractModel):
    _name = 'notification.manager'
    _description = 'Notification Manager'


    def send_push_notification(
        self,
        user_ids,
        title,
        message,
        notification_type='info',
        sticky=False
    ):

        users = self.env['res.users'].browse(user_ids)

        if not users:
            _logger.warning("No users found.")
            return False

        payload = {
            'title': title,
            'message': message,
            'type': notification_type,
            'sticky': sticky,
        }

        for user in users:
            try:
                self.env['bus.bus']._sendone(
                    user.partner_id,
                    'simple_notification',
                    payload
                )

                _logger.info(
                    "Notification sent to %s",
                    user.name
                )

            except Exception as e:
                _logger.exception(
                    "Notification failed for %s: %s",
                    user.name,
                    e
                )

        return True
    


## How to use: ##

# self.env['notification.manager'].send_push_notification(
#     user_ids=[self.env.user.id],
#     title="Success",
#     message="Record created successfully.",
#     notification_type='success',
#     sticky=False
# )


# @api.model
# def create(self, vals):
#     record = super().create(vals)
#     record.env['notification.manager'].send_push_notification(
#         user_ids=[record.user_id.id],
#         title="New Lead Assigned",
#         message=f"Lead '{record.name}' assigned to you.",
#         notification_type='info',
#         sticky=True
#     )
#     return record


## send Multiple Users ##
# users = self.env['res.users'].search([
#     ('share', '=', False)
# ])

# self.env['notification.manager'].send_push_notification(
#     user_ids=users.ids,
#     title="System Maintenance",
#     message="Server restart at 10 PM.",
#     notification_type='warning',
#     sticky=True
# )