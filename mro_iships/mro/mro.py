# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 CodUP (<http://codup.com>).
#
##############################################################################

import time
from odoo import api, fields, models, _
from odoo import netsvc
import odoo.addons.decimal_precision as dp

class mro_audit_type(models.Model):
    _name ='mro.audit_type'
    _description = 'Tipo de Auditoria'

    name = fields.Char('Tipo Auditoria', size=64)

class mro_audit_category(models.Model):
    _name = 'mro.audit_category'
    _description = 'Categorias de Auditoria'
    name = fields.Char('Categoria', size=64)

class mro_audit_subcategory(models.Model):
    _name = 'mro.audit_subcategory'
    _description = 'Subcategorias'
    name = fields.Char('Subcategory', size=64)

class mro_audit_task(models.Model):
    _name = 'mro.audit_task'
    _description = 'Tareas resultado de an hallazgo'
    name = fields.Char('Task', size=64)


class mro_request(models.Model):
    _name = 'mro.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('claim', 'Claim'),
        ('run', 'Execution'),
        ('done', 'Done'),
        ('reject', 'Rejected'),
        ('cancel', 'Canceled')
    ]

    ISSUE_LEVEL = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('critico', 'Crítico'),

    ]

    """@api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'claim':
            return 'mro.mt_request_sent'
        elif 'state' in init_values and self.state == 'run':
            return 'mro.mt_request_confirmed'
        elif 'state' in init_values and self.state == 'reject':
            return 'mro.mt_request_rejected'
        return super(mro_request, self)._track_subtype(init_values)
    """
    name = fields.Char('Reference', size=64)
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True,
         track_visibility='onchange', default='draft')

    new_field_id = fields.Many2one(comodel_name="", string="", required=False, )
    issue_level = fields.Selection(ISSUE_LEVEL, 'Nivel Hallazgo',
                             track_visibility='onchange', default='bajo')

    audit_type_id = fields.Many2one('mro.audit_type', 'Tipo Auditoria', required=True,  states={'draft': [('readonly', False)]})
    audit_category_id = fields.Many2one('mro.audit_category', 'Categoria', required=True,  states={'draft': [('readonly', False)]})
    audit_subcategory_id = fields.Many2one('mro.audit_subcategory', 'Subcategoria', required=True,  states={'draft': [('readonly', False)]})
    audit_task_id = fields.Many2one('mro.audit_task', 'Tarea', required=True,  states={'draft': [('readonly', False)]})

    asset_id = fields.Many2one('asset.asset', 'Asset', required=True, readonly=True, states={'draft': [('readonly', False)]})
    cause = fields.Char('Cause', size=64, translate=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text('Description', required=True, readonly=True, states={'draft': [('readonly', False)]})
    reject_reason = fields.Text('Reject Reason', readonly=True)
    requested_date = fields.Datetime('Requested Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Date requested by the customer for maintenance.", default=time.strftime('%Y-%m-%d %H:%M:%S'))
    execution_date = fields.Datetime('Execution Date', required=True, readonly=True, states={'draft':[('readonly',False)],'claim':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'))
    breakdown = fields.Boolean('Breakdown', readonly=True, states={'draft': [('readonly', False)]}, default=False)
    create_user_id = fields.Many2one('res.users', 'Responsible')



    @api.onchange('requested_date')
    def onchange_requested_date(self):
        self.execution_date = self.requested_date

    @api.onchange('execution_date','state')
    def onchange_execution_date(self):
        if self.state == 'draft' :
            self.requested_date = self.execution_date

    def action_send(self):
        value = {'state': 'claim'}
        for request in self:
            if request.breakdown:
                value['requested_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
            request.write(value)

    """def action_confirm(self):
        order = self.env['mro.order']
        order_id = False
        for request in self:
            order_id = order.create({
                'date_planned':request.requested_date,
                'date_scheduled':request.requested_date,
                'date_execution':request.requested_date,
                'origin': request.name,
                'state': 'draft',
                'maintenance_type': 'bm',
                'asset_id': request.asset_id.id,
                'description': request.cause,
                'problem_description': request.description,
                'request_id': request.id,
            })
        self.write({'state': 'run'})
        return order_id.id
"""
    def action_done(self):
        self.write({'state': 'done', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_reject(self):
        self.write({'state': 'reject', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mro.request') or '/'
        return super(mro_request, self).create(vals)


class mro_order(models.Model):
    """
    Maintenance Orders
    """
    _name = 'mro.order'
    _description = 'Maintenance Order'
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'DRAFT'),
        ('released', 'WAITING PARTS'),
        ('ready', 'READY TO MAINTENANCE'),
        ('done', 'DONE'),
        ('cancel', 'CANCELED')
    ]

    MAINTENANCE_TYPE_SELECTION = [
        ('bm', 'Breakdown'),
        ('cm', 'Corrective')
    ]



    name = fields.Char('Reference', size=64)
    origin = fields.Char('Source Document', size=64, readonly=True, states={'draft': [('readonly', False)]},
        help="Reference of the document that generated this maintenance order.")
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True,
        help="When the maintenance order is created the status is set to 'Draft'.\n\
        If the order is confirmed the status is set to 'Waiting Parts'.\n\
        If the stock is available then the status is set to 'Ready to Maintenance'.\n\
        When the maintenance is over, the status is set to 'Done'.", default='draft')
    maintenance_type = fields.Selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, readonly=True, states={'draft': [('readonly', False)]}, default='bm')
   # task_id = fields.Many2one('mro.task', 'Task', readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Char('Description', size=64, translate=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
    asset_id = fields.Many2one('asset.asset', 'Asset', required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_planned = fields.Datetime('Planned Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'))
    date_scheduled = fields.Datetime('Scheduled Date', required=True, readonly=True, states={'draft':[('readonly',False)],'released':[('readonly',False)],'ready':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'))
    date_execution = fields.Datetime('Execution Date', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'))
   # parts_lines = fields.One2many('mro.order.parts.line', 'maintenance_id', 'Planned parts',
    #    readonly=True, states={'draft':[('readonly',False)]})
   # parts_ready_lines = fields.One2many('stock.move', compute='_get_available_parts')
   # parts_move_lines = fields.One2many('stock.move', compute='_get_available_parts')
   # parts_moved_lines = fields.One2many('stock.move', compute='_get_available_parts')
    tools_description = fields.Text('Tools Description',translate=True)
    labor_description = fields.Text('Labor Description',translate=True)
    operations_description = fields.Text('Operations Description',translate=True)
    documentation_description = fields.Text('Documentation Description',translate=True)
    problem_description = fields.Text('Problem Description')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    company_id = fields.Many2one('res.company','Company',required=True, readonly=True, states={'draft':[('readonly',False)]}, default=lambda self: self.env['res.company']._company_default_get('mro.order'))
    #procurement_group_id = fields.Many2one('procurement.group', 'Procurement group', copy=False)
    #category_ids = fields.Many2many(related='asset_id.category_ids', string='Asset Category', readonly=True)
    #wo_id = fields.Many2one('mro.workorder', 'Work Order', ondelete='cascade')
    request_id = fields.Many2one('mro.request', 'Request')

    _order = 'date_execution'



    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mro.order') or '/'
        return super(mro_order, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('date_execution') and not vals.get('state'):
            # constraint for calendar view
            for order in self:
                if order.state == 'draft':
                    vals['date_planned'] = vals['date_execution']
                    vals['date_scheduled'] = vals['date_execution']
                elif order.state in ('released','ready'):
                    vals['date_scheduled'] = vals['date_execution']
                else: del vals['date_execution']
        return super(mro_order, self).write(vals)

