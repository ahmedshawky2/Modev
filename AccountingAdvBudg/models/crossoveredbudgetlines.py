from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class crossoveredbudgetlines (models.Model):
    _inherit = 'crossovered.budget.lines'
    x_bp_code = fields.Char(related='general_budget_id.x_bp_code')

