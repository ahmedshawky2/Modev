from odoo import models, fields, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class inovicecount(models.Model):
    _inherit = 'account.invoice'
    x_invoicecount = fields.Integer( string='# of pages', store='true',default=1)
    x_vendor_bill  = fields.Char(string="Vendor Bill #", required=False, index=True, track_visibility=False)
    x_is_Invoiced  = fields.Boolean(string="Invoiced",index=True , default = False)
    x_pst_total = fields.Monetary( 'PST' )
    x_gst_total = fields.Monetary('GST')
    x_gst_total_inv = fields.Monetary('GST INV')
    x_pst_total_inv = fields.Monetary('PST INV')

    x_inv_total = fields.Monetary(compute='inv_total', store=True, string='Total', index=True)
    x_sub_total = fields.Monetary(compute='sub_total', store=True, string='Sub Total', index=True)

    @api.onchange('invoice_line_ids')
    def _onchange_inovice_line_id(self):
        #for rec in self:
        #px= 1082
        px = 860#1015
        first = 17
        x = self.env['account.invoice.line'].search_count([('invoice_id', '=', self.id)])
        if(x<=first):
            self.x_invoicecount = 1
        else :
            self.x_invoicecount =  (int( (x-first-1)/31) +2)

    #@api.one
    @api.depends('amount_tax','amount_total')
    def onchange_amount_tax(self):
        #raise ValidationError("tet")
        _logger.debug("_onchange_amount_tax");
        self.x_gst_total_inv =0
        self.x_pst_total_inv =0;

        for r in self.tax_line_ids:
            if (r.name.startswith("GST")):
                self.x_gst_total_inv = r.amount
            elif (r.name.startswith("PST")):
                self.x_pst_total_inv = r.amount

        self.x_gst_total_inv = self.x_gst_total_inv  + self.x_gst_total
        self.x_pst_total_inv = self.x_pst_total_inv  + self.x_pst_total

    @api.one
    @api.depends('x_pst_total','x_gst_total','amount_untaxed')
    def sub_total(self):
        _logger.debug("_onchange_SUBTOTAL")
        self.x_sub_total=self.amount_untaxed #-self.x_gst_total_inv-self.x_pst_total_inv

    @api.one
    @api.depends('x_sub_total','x_gst_total_inv','x_pst_total_inv')
    def inv_total(self):
        _logger.debug("_onchange_TOTAL");
        self.x_inv_total=self.x_sub_total + self.x_gst_total_inv+self.x_pst_total_inv


'''
@api.one
def write(self, values):
    _logger.debug("_onchange_SAVE");
    res =super(inovicecount, self).write(values)
    for r in self.tax_line_ids:
        if (r.name.startswith("GST")):
            self.x_gst_total_inv = r.amount
        elif (r.name.startswith("PST")):
            self.x_pst_total_inv = r.amount
    self.x_sub_total = self.amount_untaxed - self.x_pst_total - self.x_gst_total  # -self.x_gst_total_inv-self.x_pst_total_inv
    self.x_inv_total = self.x_sub_total + self.x_pst_total + self.x_gst_total + self.x_gst_total_inv + self.x_pst_total_inv
    return  res
'''