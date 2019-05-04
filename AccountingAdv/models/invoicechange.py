from odoo import models, fields, api
from odoo import exceptions
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class groups(models.Model):
    _inherit = 'account.invoice.line'
    x_bill = fields.Many2one('account.invoice', 'Bill Number' , track_visibility=False,domain = ['&','&',('type','=','in_invoice'),('state','!=','Draft'),('x_is_Invoiced','=',False)])
    x_calc_bill_pressed = fields.Boolean(string="is Calc",index = True)
    #x_othertaxs_total = fields.Monetary('other')

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
    GSTLine  = fields.Float(string="GST", required=False)
    PSTLine = fields.Float(string="PST", required=False)




    @api.onchange('x_bill')
    def do_stuff(self):
        prod=self.env['product.product'].search([['name','=','Vendor Bill']])
        self.product_id = prod.id
        self.name = self.x_bill.number
        self.price_unit = self.x_bill.amount_untaxed

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
                vendorname = parentrecord.x_bill.partner_id.name
                ven_bill = parentrecord.x_bill.x_vendor_bill
                ven_bill_text = ""
                if ven_bill:
                    ven_bill_text = " for INV # " + ven_bill
                self.price_unit =  (float(self.MangFeesPrec)/100.0) *float(parentrecord.x_bill.amount_untaxed)
                self.name= vendorname +", "+str(self.MangFeesPrec) + '% Management Fees' +ven_bill_text



    def createproduct(self,parent_obj,product_id ,desc,unit_price,invoice_id,account_id,tax_id,parent_id,account_analytic_id ,sequence,mangfeesprec='', ismangment=False):
        parent_obj.invoice_line_ids.create({

            'product_id':product_id,
            'name': desc ,
            'price_unit': unit_price,
            'invoice_id': invoice_id,
            'account_id': account_id,
            'invoice_line_tax_ids': tax_id,
            'x_parent_id': parent_id,
            'account_analytic_id': account_analytic_id,
            'sequence':sequence+1,
            'MangFeesPrec': mangfeesprec,
            'isMangment': ismangment,


        })



    @api.multi
    def do_calc_bill(self):
        if not self.x_bill:
            raise ValidationError("No Bill");
        if self.x_calc_bill_pressed:
            raise ValidationError("Calc Button already Pressed");
        self.x_calc_bill_pressed= True

        holdbackBill= self.env['product.product'].search([['name','=','Holdback Bill']])
        holdbackInvoice = self.env['product.product'].search([['name', '=', 'Holdback Invocie']])
        mangeprod = self.env['product.product'].search([['name', '=', 'Management Fees']])
        RemainingHoldback = self.env['product.product'].search([['name', '=', 'Remaining Holdback']])
        PST = self.env['product.product'].search([['name', '=', 'PST']])
        GST = self.env['product.product'].search([['name', '=', 'GST']])
        #raise ValidationError(mangeprod)
        parent_id = self.invoice_id.id
        parent_obj = self.env['account.invoice'].browse(parent_id)

        bill_id = self.x_bill.id
        bill = self.env['account.invoice'].browse(bill_id)

        vendorname = bill.partner_id.name
        ven_bill = bill.x_vendor_bill
        bill.x_is_Invoiced = True   # change bill to be marked as Invoiced
        ven_bill_text=""
        if ven_bill:
            ven_bill_text =" INV# " + ven_bill

        for record in  self.x_bill.invoice_line_ids:
            if record.product_id.id==holdbackBill.id:
                groups.createproduct(self, parent_obj, holdbackInvoice.id,  "Less HoldBack" + ven_bill_text, record.price_unit, parent_id, holdbackInvoice.property_account_income_id.id, holdbackInvoice.taxes_id, self.id,
                              holdbackInvoice.x_analytic_account.id,self.sequence)

                self.price_unit = self.price_unit+abs(record.price_unit)
            else:
                self.name = vendorname +", " + record.product_id.name +" [" +record.product_id.default_code +"]" + ven_bill_text

            if record.product_id.id ==RemainingHoldback.id:
             #self.x_parent_id   raise ValidationError(RemainingHoldback.x_analytic_account.id)
                self.account_analytic_id=RemainingHoldback.x_analytic_account.id

        groups.createproduct(self, parent_obj, mangeprod.id, " 4% Management Fees" + ven_bill_text,
                      0.04 * float(self.x_bill.amount_untaxed),
                      parent_id,
                      mangeprod.property_account_income_id.id
                      , mangeprod.taxes_id, self.id,
                      mangeprod.x_analytic_account.id,self.sequence,
                      '4', True)

        tempgst =0
        temppst =0
        for r in self.x_bill.tax_line_ids:

            if(r.name.startswith("GST")):
                parent_obj.x_gst_total += r.amount
                tempgst +=r.amount
            elif(r.name.startswith("PST")):
                parent_obj.x_pst_total += r.amount
                temppst += r.amount

        self.GSTLine =tempgst
        self.PSTLine = temppst
        '''
        if parent_obj.x_pst_total  and parent_obj.x_pst_total>0 :
            groups.createproduct(self, parent_obj, PST.id, PST.name + ven_bill_text,
                             temppst,
                             parent_id,
                             PST.property_account_income_id.id,
                             '',
                             self.id,
                             PST.x_analytic_account.id,
                             self.sequence
                             )
        if parent_obj.x_gst_total and parent_obj.x_gst_total>0:
            groups.createproduct(self, parent_obj, GST.id, GST.name + ven_bill_text,
                             tempgst,
                             parent_id,
                             GST.property_account_income_id.id,
                             '',
                             self.id,
                             GST.x_analytic_account.id,
                             self.sequence
                             )
        '''





    @api.multi
    def unlink(self):
        holdbackInv = self.env['product.product'].search([['name', '=', 'Holdback Invocie']])
        parent_id = self.invoice_id.id
        parent_obj = self.env['account.invoice'].browse(parent_id)
        if self  and self.x_parent_id:
            if self.product_id.id == holdbackInv.id:
                p=self.env['account.invoice.line'].browse(self.x_parent_id)
                if p :
                    p.price_unit = p.price_unit - abs(self.price_unit)
            else:
                if (self.name.startswith("GST")):
                    parent_obj.x_gst_total -= abs(self.price_unit)
                elif (self.name.startswith("PST")):
                    parent_obj.x_pst_total -= abs(self.price_unit)
        else:
            if self and self.id :
                if self.x_bill:
                    self.x_bill.x_is_Invoiced = False

                    for r in self.x_bill.tax_line_ids:
                        if (r.name.startswith("GST")):
                            parent_obj.x_gst_total -= r.amount
                        elif (r.name.startswith("PST")):
                            parent_obj.x_pst_total -= r.amount

                p = self.env['account.invoice.line'].search([['x_parent_id','=',self.id]])
                try:
                    #p.unlink()
                    for p1 in p:
                        if p1:
                            p1.unlink()


                except:
                    pass
                    #_logger("err")


        return models.Model.unlink(self)


        #raise ValidationError("Done")


'''
    @api.multi
    def unlink(self,values):
        raise ValidationError("No Delete")
        campus_unlink = super(groups,self).unlink(values)
        return campus_unlink

'''

