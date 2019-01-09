from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class productchanges(models.Model):
    _inherit = 'product.product'
    x_analytic_account = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account", required=False)
