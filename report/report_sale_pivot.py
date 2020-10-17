# -*- coding: utf-8 -*-
# @author Carlos A. Garcia

from odoo import tools
from odoo import api, fields, models


class SaleReportPivot(models.Model):
    _inherit = "sale.report"
    _description = "Reporte Pivote"

    serial_id = fields.Many2one('res.serial', string='Numero de Serie', readonly=True)
    contract_id = fields.Many2one('res.contract', string='Numero de Contrato', readonly=True)
    product_serv_id = fields.Many2one('product.product', string='Servicio de Renta', readonly=True)
    type = fields.Selection([
        ('prepay', 'Prepago'),
        ('plan', 'Plan'),
        ('activation', 'Activación'),
    ], string='Tipo de Venta', readonly=True)
    protection = fields.Selection([
        ('0', 'Ninguno'),
        ('55', 'Protección 55'),
        ('105', 'Protección 105'),
        ('155', 'Protección 155'),
    ], string='Proteccion de Equipo', readonly=True)

    repo_fields = {
        'type': ',l.type as type',
        'serial': ',l.serial_id as serial_id',
        'contract': ',l.contract_id as contract_id',
        'prod_rent': ',l.product_serv_id as product_serv_id',
        'protection': ',l.protection as protection',
    }
    repo_groupby = ",l.serial_id,l.contract_id,l.type,l.product_serv_id,l.protection"

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table,
                                                                       self._query(fields=self.repo_fields,
                                                                                   groupby=self.repo_groupby)
                                                                       ))
