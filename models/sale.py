# -*- coding: utf-8 -*-
# @author Carlos A. Garcia

from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)


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

    type = fields.Selection(SALE_TYPE_SELECTION, string='Tipo')
    serial_id = fields.Many2one('res.serial', string='Numero de serie')
    contract_id = fields.Many2one('res.contract', string='Numero de Contrato')
    price_rent = fields.Float(string='Precio Renta')
    protection = fields.Selection(PROTECTION_SELECTION, string='Proteccion de equipo')
    product_serv_id = fields.Many2one('product.product', string='Servicio')

    @api.onchange('product_serv_id')
    def _onchange_product_serv_id(self):
        self.price_rent = self.product_serv_id.lst_price

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            taxes_rent_included = 0
            taxes_rent_excluded = 0
            price_tax_rent = 0
            if line.type == 'activation':
                taxes_rent = line.tax_id.compute_all(line.price_rent, line.order_id.currency_id, 1,
                                                     product=line.product_serv_id, partner=line.order_id.partner_shipping_id)
                taxes_rent_included = taxes_rent['total_included']
                taxes_rent_excluded = taxes_rent['total_excluded']
                price_tax_rent = sum(t.get('amount', 0.0) for t in taxes_rent.get('taxes', []))
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])) + price_tax_rent,
                'price_total': taxes['total_included'] + taxes_rent_included,
                'price_subtotal': taxes['total_excluded'] + taxes_rent_excluded,
            })

    def add_line_wizard(self):
        auto_deliver = False
        if self.type in ('prepay', 'activation'):
            auto_deliver = True
            quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                    ('company_id', '=', self.company_id.id),
                                                    ('quantity', '>', 0)])
            if not quant:
                raise UserError('No existe stock disponible para el Producto seleccionado!')
        new_line = [(0, 0, {
            'order_id': self.order_id.id,
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
        sale.write({'order_line': new_line, 'auto_deliver': auto_deliver})
        return {'type': 'ir.actions.act_window_close'}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    auto_deliver = fields.Boolean("Auto Entrega", default=False)

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

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.auto_deliver:
            picking = self.env['stock.picking'].search([('sale_id', '=', self.id),
                                                        ('company_id', '=', self.company_id.id),
                                                        ('state', 'not in', ('cancel', 'done'))
                                                        ])
            if picking:
                if picking.move_line_ids_without_package:
                    for move in picking.move_line_ids_without_package:
                        move.write({'qty_done': move.move_id.product_uom_qty})
                elif picking.move_line_ids:
                    for move in picking.move_line_ids:
                        move.write({'qty_done': move.move_id.product_uom_qty})
                picking.action_done()
        return res
