# -*- coding: utf-8 -*-
# @author Carlos A. Garcia

from odoo import api, fields, models, _


class ResContract(models.Model):
    _name = 'res.contract'
    _description = 'Número de Contrato'

    name = fields.Char(string="Numero de Contrato", required=True)
    date_start = fields.Date(string='Fecha Inicio', default=fields.Date.today(), required=True)
    date_end = fields.Date(string='Fecha Fin')
