from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _get_context(self):
        """
        Forcefully change 'Asia/Calcutta' to 'Asia/Kolkata' in the context
        to avoid PostgreSQL errors on servers missing the 'Asia/Calcutta' alias.
        """
        res = super()._get_context()
        if res.get('tz') == 'Asia/Calcutta':
            res['tz'] = 'Asia/Kolkata'
        return res
