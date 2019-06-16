# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import tools

STATE_COLOR_SELECTION = [
    ('0', 'Red'),
    ('1', 'Green'),
    ('2', 'Blue'),
    ('3', 'Yellow'),
    ('4', 'Magenta'),
    ('5', 'Cyan'),
    ('6', 'Black'),
    ('7', 'White'),
    ('8', 'Orange'),
    ('9', 'SkyBlue')
]




class asset_category(models.Model):
    _description = 'Asset Tags'
    _name = 'asset.category'

    name = fields.Char('Category', required=True, translate=True)
    #If not necessary cuause de relation has changed to ManyToOne
    #asset_ids = fields.Many2many('asset.asset', id1='category_id', id2='asset_id', string='Assets')


class asset_asset(models.Model):
    """
    Assets
    """
    _name = 'asset.asset'
    _description = 'Asset'
    _inherit = ['mail.thread']




    name = fields.Char('Asset Name', size=64, required=True, translate=True)
    asset_number = fields.Char('Asset Number', size=64)
    # responsible line was moved down to modifications
    active = fields.Boolean('Active', default=True)
    is_leased = fields.Boolean('is leased?', default=False)
    has_issues = fields.Boolean('has Issues?', default=False)
    contract_date = fields.Date('lease Date')
    leasing_start_date = fields.Date('leasing Start')
    leasing_end_date = fields.Date('leasing End')
    image = fields.Binary("Image")
    image_small = fields.Binary("Small-sized image")
    image_medium = fields.Binary("Medium-sized image")
    #Changed from many to many to Many2One
    category_id = fields.Many2one('asset.category', string='Category')
    #Modifications
    responsible_id = fields.Many2one('res.users', 'Responsible ', track_visibility='onchange')
    assigned_id = fields.Many2one('res.users', 'Assigned to', track_visibility='onchange')
    owner_id = fields.Many2one('res.partner', 'Owner')
    customer_id = fields.Many2one('res.partner', 'Customer')
    parent_id = fields.Many2one('asset.asset', 'Parent')





    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(asset_asset, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(asset_asset, self).write(vals)
