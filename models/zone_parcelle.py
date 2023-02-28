import datetime
import requests
import json
import os
from requests.auth import HTTPBasicAuth
from odoo import api, fields, models, _
from odoo import exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning



class ZoneParcelle(models.Model):
    _name = "zone.parcelle"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "ZoneLot de Parcelle"

    name = fields.Char(string="Nom du Zone")
    projetparcelle_id = fields.Many2one('projet.parcelle', 'Projet',required=True , tracking=True) 
    description = fields.Text(string="Description")
    
    _sql_constraints = [('zone_parcelle_uniq', 'unique(name)', 'Le nom du zone lot doit être unique !')]

    
