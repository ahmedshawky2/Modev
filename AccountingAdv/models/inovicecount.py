from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class inovicecount(models.Model):
    _inherit = 'account.invoice'
    x_invoicecount = fields.Integer( string='# of pages', store='true',default=1)

    @api.onchange('invoice_line_ids')
    def _onchange_inovice_line_id(self):
        #for rec in self:
        #px= 1082
        px = 1015
        first = 17
        x = self.env['account.invoice.line'].search_count([('invoice_id', '=', self.id)])
        if(x<=first):
            self.x_invoicecount = 1
        else :
            self.x_invoicecount =  (int( (x-first-1)/31) +2)



