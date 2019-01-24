from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class badgetpost (models.Model):
    _inherit = 'account.budget.post'
    x_bp_code  = fields.Char(string="Code", required=False, index=False, track_visibility=False)

