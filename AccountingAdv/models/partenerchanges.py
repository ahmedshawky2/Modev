from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class partenerchanges(models.Model):
    _inherit = 'res.company'
    x_headerimage = fields.Binary("Header Image", attachment=True,help="Header Image")
