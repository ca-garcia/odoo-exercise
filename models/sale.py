# -*- coding: utf-8 -*-
# @author Carlos A. Garcia

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    SALE_TYPE_SELECTION = [
        ('prepay', 'Prepago'),
        ('plan', 'Plan'),
        ('activation', 'Activación'),
    ]

    PROTECTION_SELECTION = [
        ('0', 'Ninguno'),
        ('55', 'Protección 55'),
        ('105', 'Protección 105'),
        ('155', 'Protección 155'),
    ]

    type = fields.Selection(SALE_TYPE_SELECTION, string='Tipo', required=True)
    serial_id = fields.Many2one('res.serial', string='Numero de serie')
    contract_id = fields.Many2one('res.contract', string='Numero de Contrato')
    price_rent = fields.Float(string='Precio Renta', default=0)
    protection = fields.Selection(PROTECTION_SELECTION, string='Proteccion de equipo ')
    product_serv_id = fields.Many2one('product.product', string='Servicio')

    def add_line_wizard(self):
        new_line = [(0, 0, {
            'type': self.type,
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'price_unit': self.price_unit,
            'tax_id': [(6, 0, self.tax_id.ids)],
            'serial_id': self.serial_id.id,
            'contract_id': self.contract_id.id,
            'product_serv_id': self.product_serv_id.id,
            'protection': self.protection,
            'price_rent': self.price_rent,
        })]
        sale = self.env['sale.order'].search([('id', '=', self.order_id.id)])
        sale.write({'order_line': new_line})
        return {'type': 'ir.actions.act_window_close'}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def select_line_wizard(self):
        return {
            'name': "Tipo de Venta",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'view_id': self.env.ref('odoo_exercise.sale_order_line_custom_view').id,
            'target': 'new',
            'context': {'default_order_id': self.id}
        }
