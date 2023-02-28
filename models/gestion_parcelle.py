import datetime
import requests
import json
import os
from requests.auth import HTTPBasicAuth
from odoo import api, fields, models, _
from odoo import exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class GestionParcelle(models.Model):
    _name = "gestion.parcelle"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Gestion de Parcelle"
    _rec_name='lot'

   
    zone = fields.Char(string="Zone", required=True)
    client_id = fields.Many2one('res.partner', 'Propriétaire', tracking=True,  size=32)
    sale_order_id = fields.Many2one('sale.order', 'Bon de commande', tracking=True,  size=32)
    lot = fields.Char(string="N° LOT de parcelle", size=32, tracking=True)

    Goudron  = fields.Char(string="Goudron ", size=32)
    largeur  = fields.Char(string="Largeur ", size=32)
      

    sup = fields.Float(string="Supperficie", tracking=True)
    type_parcelle = fields.Selection([
        ('RT', 'Retraite'),
        ('CM', 'Congé de Maternité'),
        ('AT', 'Accident de Travail'),
        ('PF', 'Prestation familiale')],
         'Type de parcelle', default='RT')

    prix = fields.Float(string="Prix")
    zoneparcelle_id = fields.Many2one('zone.parcelle', 'Zone Lot',required=True , tracking=True)
    projetparcelle_id = fields.Many2one('projet.parcelle', 'Projet',required=True , tracking=True) 
    
    status = fields.Selection([
        ('cancelled', 'Annulé'),
        ('draft', 'Créé'),
        ('process', 'En Traitement'),
        ('invoiced', 'En Facturation'),
        ('paid', 'Payer')
    ], 'Statut de parcelle', default='draft')
    
    parcelle_state_vente = fields.Selection([
        ('libre', 'Libre'),
        ('process', 'En Vente'),
        ('reserve', 'Réserver'),
        ('invoiced_draft', 'Facturé'),
        ('invoiced_posted', 'Facturé'),
        ('partial', 'Partiel'),
        ('paid', 'Payé')
    ], 'State de parcelle', default='libre')

    email= fields.Char(string="Email", tracking=True)
    telephone = fields.Char(string="Téléphone", tracking=True)
    
    date_depot = fields.Date(string="Date de dépôt")
    reserver = fields.Boolean('Reserver ?')
    
    numero_parcelle = fields.Char(string="Numero Parcelle", tracking=True)

    vocation = fields.Selection([
        ('IJ', 'IJ'),
        ('IS', 'IS'),
        ('MIX', 'MIX'),
        ('IB', 'IB')
    ])

    def btn_annuler(self):
        res = []

        modelObj = self.env['sale.order']
        for record in self:
            rec = modelObj.search([('lot', '=', record.id)])
            print(rec)
            if rec: #or rec.state != 'cancel':
                raise ValidationError(_('Veuillez annuler le devis relier a cette parcelle pour mettre en ventre le lot.'))
            else:
                print('********** btn_annuler')
                self.update({"status": 'draft'})
                self.update({"parcelle_state_vente": 'libre'})
        return res

    def action_view_client_id(self):
        result = self.env['ir.actions.act_window']._for_xml_id('contacts.action_contacts')
        result['views'] = [(self.env.ref('base.view_partner_form', False).id, 'form')]
        result['res_id'] = self.client_id.id
        return result

    def action_view_sale_order_lot(self):
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
        result['res_id'] = self.sale_order_id.id
        print('********************* sale_order_id ', self.sale_order_id)
        return result


    
    @api.model
    def create(self, vals):
        
#        seq = self.env["ir.sequence"].next_by_code("suivi.courrier.seq") or 0
#        vals["refcourrier"] = seq
#        print("************************************************* newwwwwwww *********************************", vals["refcourrier"])
#        result = super(SuiviCourrier, self).create(vals)
        return super().create(vals)

#         seq = self.env["ir.sequence"].next_by_code("suivi.courrier") or 0
#         vals["sequence"] = seq
#         return super().create(vals)
  

    @api.onchange('projetparcelle_id')
    def onchange_zone(self):
        return {'domain': {'zoneparcelle_id': [('projetparcelle_id', '=', self.projetparcelle_id.id)]}}

    def mettre_envente(self):
        print("******** change statut parcelle en En vente")
        if self.status != 'draft':
            if self.status == 'process':
                raise UserError(_('Cette parcelle et en Traitement !!!'))
            if self.status == 'paid':
                raise UserError(_('Cette parcelle et PAYER !!!'))
            if self.status == 'invoiced':
                raise UserError(_('Cette parcelle et en Facturation !!!'))


            raise UserError(_('Cette parcelle ne peut pas être EN VENTE !!!'))

        return self.update({"status": 'process'})
    
