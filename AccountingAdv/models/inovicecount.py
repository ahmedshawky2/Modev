from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class inovicecount(models.Model):
    _inherit = 'account.invoice'
    x_invoicecount = fields.Integer(compute="associate_count", string='# of Associate', store='true')

    @api.depends('invoice_line_ids')
    def associate_count(self):
        for rec in self:
            #px= 1082
            px = 1050
            first = 17  
            x = self.env['account.invoice.line'].search_count([('invoice_id', '=', rec.id)])
            if(x<=first):
                rec.x_invoicecount = 1 * px
            else :
                rec.x_invoicecount =  (int( (x-first-1)/31) +2)*px



