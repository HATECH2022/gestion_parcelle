
from odoo import api, fields, models, _
from _datetime import date
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from _datetime import date
#from mock.mock import self

class parcelle_sale_order(models.Model):
    _name='sale.order'
    _rec_name='lot'
    _inherit = 'sale.order'
    
    projetparcelle_id = fields.Many2one('projet.parcelle','Projet du parcelle')
    zoneparcelle_id = fields.Many2one('zone.parcelle', 'Zone Lot')
    lot = fields.Many2one('gestion.parcelle','N° LOT de parcelle')

    @api.model
    def create(self, values):
        print("**************************** create ", values['lot'])
        Parcel = self.env['gestion.parcelle'].search([('id', '=', values['lot'])])
        Parcel.update({"status": 'process'})
        Parcel.update({"parcelle_state_vente": 'process'})
        if Parcel.status != 'process':
            Parcel.update({"status":'process'})
        if Parcel.parcelle_state_vente != 'process':
            Parcel.update({"parcelle_state_vente": 'process'})
        print("**************************** create ", Parcel)
        return super(parcelle_sale_order, self).create(values)


   
   # lot_id = fields.Many2one(compute='_compute_lot_id', comodel_name='gestion.parcelle', string='Lot', store=True)
   # lot_zone = fields.Many2one(compute='_compute_lot_zone', comodel_name='zone.parcelle', string='Zone', store=True)

   # @api.depends('invoice_line_ids')
   # def _compute_lot_id(self):
    #    self.lot_id = self.invoice_line_ids.sale_line_ids.order_id.lot

   # @api.depends('invoice_line_ids')
   # def _compute_lot_zone(self):
   #     self.lot_zone = self.invoice_line_ids.sale_line_ids.order_id.lot.zoneparcelle_id
    
    def add_autolines(self):
        print("******** COMPLETER LE DEVIS ***********")
        proprietaire = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        if not proprietaire:
            raise UserError(_("Merci de compléter cette devis"))
        else:
            #parcelle = self.env['gestion.parcelle'].search([('lot', '=', self.lot)])
            print("******** PARCELLE ", self.lot)
            quantity = self.lot.sup
            Parcel = self.env['product.product'].search([('default_code', '=', 'TERRAIN')])
            self.env['sale.order.line'].with_context().create({
                'order_id': self.id,
                'name': Parcel.name,
                'product_id': Parcel.id,
                'product_uom_qty': quantity,
                'price_unit': Parcel.standard_price,
                
            })
        # if self.lot.status != 'process':
        #     self.lot.update({"status":'process'})
        # if self.lot.parcelle_state_vente != 'process':
        #     self.lot.update({"parcelle_state_vente": 'process'})
        return self

    def action_confirm(self):
        res = super(parcelle_sale_order, self).action_confirm()
        self.lot.update({"parcelle_state_vente": 'reserve'})
        print('****************************** action_confirm')
        print('********************************** partner_id ', self.partner_id)
        self.lot.update({"client_id" : self.partner_id})
        self.lot.update({"sale_order_id": self})
        return res

    def _action_cancel(self):
        print('************************** action_cancle')
        self.lot.client_id = False
        self.lot.sale_order_id = False
        self.lot.update({"status": 'draft'})
        self.lot.update({"parcelle_state_vente": 'libre'})
        res = super(parcelle_sale_order, self)._action_cancel()
        return res

    def action_draft(self):
        res = super(parcelle_sale_order, self).action_draft()
        if self.lot.status == 'draft':
            self.lot.update({"status": 'process'})
            self.lot.update({"parcelle_state_vente": 'process'})
            return res
        else:
            raise UserError(_("Il y a déja un devis pour ce lot"))

    def _compute_is_expired(self):
        dateNow = fields.Date.today()
        # print('*************************** ', dateNow)

        res = super(parcelle_sale_order, self)._compute_is_expired()
        return res

    @api.onchange('projetparcelle_id')
    def onchange_zone(self):
        return {'domain': {'zoneparcelle_id': [('projetparcelle_id', '=', self.projetparcelle_id.id)]}}
    
    @api.onchange('zoneparcelle_id')
    def onchange_lot(self):
        return {'domain': {'lot': [('zoneparcelle_id', '=', self.zoneparcelle_id.id), ('status','=','draft')]}}

class SaleAdvancePaymentInv(models.TransientModel):
    _name = 'sale.advance.payment.inv'
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        print('****************************** _create_invoice')
        print('**************************************', self.sale_order_ids.lot)
        self.sale_order_ids.lot.update({"status": 'invoiced'})
        self.sale_order_ids.lot.update({"parcelle_state_vente": 'invoiced_draft'})
        return res

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        print('************************* action_post')
        source_orders = self.line_ids.sale_line_ids.order_id
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        print('*************************** source_orders ',source_orders.lot)
        source_orders.lot.update({"parcelle_state_vente": 'invoiced_posted'})
        return res
    
    lot_id = fields.Many2one(compute='_compute_lot_id', comodel_name='gestion.parcelle', string='Lot', store=True)
    lot_zone = fields.Many2one(compute='_compute_lot_zone', comodel_name='zone.parcelle', string='Zone', store=True)
    supp = fields.Many2one(compute='_compute_supp', comodel_name='zone.parcelle', string='Supperficie', store=True)

    @api.depends('invoice_line_ids')
    def _compute_lot_id(self):
        for record in self:
            record.lot_id = record.invoice_line_ids.sale_line_ids.order_id.lot

    @api.depends('invoice_line_ids')
    def _compute_lot_zone(self):
        for record in self:
            record.lot_zone = record.invoice_line_ids.sale_line_ids.order_id.lot.zoneparcelle_id
           
    @api.depends('invoice_line_ids')
    def _compute_supp(self):
        for record in self:
            record.supp = record.invoice_line_ids.sale_line_ids.order_id.lot.sup
   
    def action_register_payment(self):
         # print('*************************** action_register_payment ', self.payment_difference)
         print('************************* self', self.line_ids)
         res = super(AccountMove, self).action_register_payment()
         source_orders = self.line_ids.sale_line_ids.order_id
        # source_orders.lot.update({"status": 'paid'})
       #  source_orders.lot.update({"parcelle_state_vente": 'payed'})
         return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        # print('**************************** action_create_payments ',
        #       '1 ', self.env['account.move'],
        #       '2 ', self.line_ids,
        #       '3 ', self.env['account.move.line'],
        #       '4 ', self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids,
        #       '5 ', self.env['account.move.line'].browse(self._context.get('active_ids', []))
        #       )
        print('******************************** 4 lot', self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids.sale_line_ids.order_id.lot)
        source_orders = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids.sale_line_ids.order_id
        source_orders.lot.update({"status": 'paid'})
        if self.payment_difference == 0:
            source_orders.lot.update({"parcelle_state_vente": 'paid'})
            print('************************************************ Paid')

        else:
            source_orders.lot.update({"parcelle_state_vente": 'partial'})
            print('************************************************ Partially Paid')
        res = super(AccountPaymentRegister, self).action_create_payments()
        return res
