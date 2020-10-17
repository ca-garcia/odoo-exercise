# -*- coding: utf-8 -*-
# @author Carlos A. Garcia

from odoo import api, fields, models, _


class ResSerial(models.Model):
    _name = 'res.serial'
    _description = 'Número de serie'

    name = fields.Char(string="Numero de serie")
