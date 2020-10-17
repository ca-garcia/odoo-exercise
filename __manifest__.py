# -*- coding: utf-8 -*-
{
    'name': 'Ejercicio para Odoo Developer',
    'version': '1.0',
    'category': 'Extra',
    'author': 'Carlos A. García',
    'website': '',
    'summary': 'Ejercicio para Odoo Developer',
    'description': """ 
    """,
    'depends': [
        'sale',
        'sales_team',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'report/report_saleorder_pdf.xml',
        'report/report_sale_pivot_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
