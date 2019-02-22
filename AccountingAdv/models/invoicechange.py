from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class groups(models.Model):
    _inherit = 'account.invoice.line'
    x_bill = fields.Many2one('account.invoice', 'Bill Number' , track_visibility=False,domain = [('type','=','in_invoice'),('state','!=','Draft')])

    #x_bill_name = fields.Many2one('account.invoice', string='Bill Number', related = 'x_bill.sequence_number_next')
    x_parent_id  = fields.Integer(string="Parent Line Id", required=False ,index=True)
    MangFeesPrec = fields.Selection(
        selection=[
            ('4', '4 %'),
            ('2', '2 %'),
            ('8', '8 %')
        ],
        string='Management Fees %')
    isMangment = fields.Boolean(string="isMang")




    @api.onchange('x_bill')
    def do_stuff(self):
        prod=self.env['product.product'].search([['name','=','Vendor Bill']])
        self.product_id = prod.id
        self.name = self.x_bill.number
        self.price_unit = self.x_bill.amount_total_signed

    @api.onchange('product_id')
    def prodcutchange(self):
        prod=self.env['product.product'].search([['id', '=', self.product_id.id]])
        if prod :
            self.account_analytic_id=prod.x_analytic_account.id

    @api.onchange('MangFeesPrec')
    def MangemnetChange(self):

        if self.MangFeesPrec and self.product_id.name != "Management Fees":
            raise ValidationError("Can't Set Percentage for this Product");

        if self.MangFeesPrec and self.x_parent_id:
            parentrecord = self.env['account.invoice.line'].search([['id', '=', self.x_parent_id]])
            if parentrecord:
                self.price_unit =  (float(self.MangFeesPrec)/100.0) *float(parentrecord.x_bill.amount_untaxed)
                self.name= str(self.MangFeesPrec) + ' % Management Fees  ' + "for " +str(parentrecord.x_bill.number)






    @api.multi
    def do_calc_bill(self):
        if not self.x_bill:
            raise ValidationError("No Bill");

        holdbackBill= self.env['product.product'].search([['name','=','Holdback Bill']])
        holdbackInvoice = self.env['product.product'].search([['name', '=', 'Holdback Invocie']])
        mangeprod = self.env['product.product'].search([['name', '=', 'Management Fees']])
        RemainingHoldback = self.env['product.product'].search([['name', '=', 'Remaining Holdback']])
        #raise ValidationError(mangeprod)
        parent_id = self.invoice_id.id
        parent_obj = self.env['account.invoice'].browse(parent_id)

        bill_id = self.x_bill.id
        bill = self.env['account.invoice'].browse(bill_id)
        vendorname = bill.partner_id.name;

        for record in  self.x_bill.invoice_line_ids:
            if record.product_id.id==holdbackBill.id:
                parent_obj.invoice_line_ids.create({

                    'product_id': holdbackInvoice.id,
                    'name':"HoldBack" + " for " +self.x_bill.number  ,
                    'price_unit':record.price_unit,
                    'invoice_id':parent_id,
                    'account_id':holdbackInvoice.property_account_income_id.id,
                    'invoice_line_tax_ids':holdbackInvoice.taxes_id,
                    'x_parent_id':self.id,
                    'account_analytic_id':holdbackInvoice.x_analytic_account.id

                })
                self.price_unit = self.price_unit+abs(record.price_unit)
            else:
                self.name = vendorname +" : " + record.product_id.name +" [" +record.product_id.default_code +"]"

            if record.product_id.id ==RemainingHoldback.id:
             #self.x_parent_id   raise ValidationError(RemainingHoldback.x_analytic_account.id)
                self.account_analytic_id=RemainingHoldback.x_analytic_account.id

        parent_obj.invoice_line_ids.create({

            'product_id': mangeprod.id,
            'name': '4% Management Fees  '+ "for " +self.x_bill.number,

            'price_unit': 0.04*float(self.x_bill.amount_untaxed),
            'MangFeesPrec':'4',
            'isMangment' :True,
            'invoice_id': parent_id,
            'account_id': mangeprod.property_account_income_id.id,
            'invoice_line_tax_ids': mangeprod.taxes_id,
            'x_parent_id': self.id,
            'account_analytic_id': mangeprod.x_analytic_account.id

        })



    @api.multi
    def unlink(self):
        holdbackInv = self.env['product.product'].search([['name', '=', 'Holdback Invocie']])
        if self  and self.x_parent_id:
            if self.product_id.id == holdbackInv.id:
                p=self.env['account.invoice.line'].browse(self.x_parent_id)
                if p :
                    p.price_unit = p.price_unit - abs(self.price_unit)
        else:
            if self and self.id :
                p = self.env['account.invoice.line'].search([['x_parent_id','=',self.id]])
                try:
                    #p.unlink()
                    for p1 in p:
                        if p1:
                            p1.unlink()


                except:
                    _logger("err")


        return models.Model.unlink(self)


        #raise ValidationError("Done")


'''
    @api.multi
    def unlink(self,values):
        raise ValidationError("No Delete")
        campus_unlink = super(groups,self).unlink(values)
        return campus_unlink

'''

