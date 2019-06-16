# -*- coding: utf-8 -*-
{
    'name': "Assets",
     'summary': """
        Asset Management for industrial ships and building like hotels or bussines buildings
        """,

    'description': """
Managing Assets in Odoo.
===========================
Support following feature:
    * Location for Asset
    * Assign Asset to employee (for Responsible)
    * Assign Asset to customer (leaseholder)
    * Manage rental contracts
    * Track warranty information
    * Custom states of Asset
    * States of Asset for different team: Finance, Warehouse, Manufacture, Maintenance and Accounting
    * Drag&Drop manage states of Asset
    * Asset Tags
    * Search by main fields
    """,
    'author': "outis",
    'website': "http://www.outis.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Industry',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
       # 'data/stock_data.xml',
    ],

}