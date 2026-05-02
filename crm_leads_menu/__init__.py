from . import models
from . import wizard
from odoo import api, SUPERUSER_ID

def _post_init_hook(env):
    """
    Update existing users to use 'Asia/Kolkata' instead of 'Asia/Calcutta'.
    'Asia/Calcutta' is often not recognized by newer PostgreSQL installations.
    """
    env.cr.execute("UPDATE res_users SET tz = 'Asia/Kolkata' WHERE tz = 'Asia/Calcutta'")