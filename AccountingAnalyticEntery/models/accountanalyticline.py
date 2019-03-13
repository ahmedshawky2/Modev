from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class accountanalyticline(models.Model):
    _inherit = 'account.analytic.line'
    x_studio_pst = fields.Monetary( 'PST' )
    x_studio_gst = fields.Monetary('GST')


