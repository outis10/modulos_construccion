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

    mro_audit_category_ids = fields.Many2many(
        'mro.audit_category',
        'audit_type_category_m2m',
        'audit_type_id',
        'audit_category_id',
        'Categorias', )


class mro_audit_category(models.Model):
    _name = 'mro.audit_category'
    _description = 'Categorias de Auditoria'
    name = fields.Char('Categoria', size=64)

    mro_audit_subcategory_ids = fields.Many2many(
        'mro.audit_subcategory',
        'audit_category_subcategory_m2m',
        'audit_category_id',
        'audit_subcategory_id',
        'Tipos de Subcategoria', )


class mro_audit_subcategory(models.Model):
    _name = 'mro.audit_subcategory'
    _description = 'Subcategorias'
    name = fields.Char('Subcategoria', size=64)
    #mro_audit_category_id = fields.Many2one('mro.audit_category', 'Categoria', required=False, )



class mro_audit_area_afectacion(models.Model):
    _name = 'mro.audit_area_afectacion'
    _description = 'Area afectacion'
    name = fields.Char('Área afectación', size=64)


class mro_issue(models.Model):
    _name = 'mro.audit_issue'
    _description = 'Lista de hallazgos'
    _rec_name = 'hallazgo'


    mro_audit_type_id = fields.Many2one('mro.audit_type', 'Tipo Auditoria', required=True, )
    mro_audit_category_id = fields.Many2one('mro.audit_category', 'Categoria', required=True, )
    mro_audit_subcategory_id = fields.Many2one('mro.audit_subcategory', 'Subcategoria',  required=True, )
    mro_audit_area_afectacion_id= fields.Many2one('mro.audit_area_afectacion', 'Área afectación', required=True, )
    #category = fields.Char('Categoria', size=64)
    #subcategoria = fields.Char('Subcategoria', size=64)
    #afectacion = fields.Char('Categoria', size=64)
    hallazgo = fields.Char('Hallazgo', size=64)


class mro_audit(models.Model):
    _name = 'mro.audit'
    _description = 'Audit'
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Realizada'),
        ('accepted', 'Aceptada'),

    ]

    name = fields.Char('Referencia', size=64)
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True,
                             track_visibility='onchange', default='draft')
    asset_id = fields.Many2one('asset.asset', 'Activo', domain=[('category_id.name', '=', "Edificio")],
                               required=True, readonly=True,
                               states={'draft': [('readonly', False)]})

    audit_type_id = fields.Many2one('mro.audit_type', 'Tipo Auditoria', required=True,
                                    states={'draft': [('readonly', False)]})

    description = fields.Text('Descripción', readonly=True, states={'draft': [('readonly', False)]})
    execution_date = fields.Datetime('Fecha solicitud', required=True, readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     default=time.strftime('%Y-%m-%d %H:%M:%S'))
    create_user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self._uid)
    mro_request_ids = fields.One2many('mro.request', 'mro_audit_id', string="Hallazgos", required=False, )



    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('mro.audit') or '/'
        return super(mro_audit, self).create(vals)

    def open_one2many_request(self, vals):
        context = {'default_asset_id': self.asset_id.id, 'default_mro_audit_id': self.id,
                   'default_audit_type_id': self.audit_type_id.id}
        print(context)
        return {

             'type': 'ir.actions.act_window',

             'name': 'Hallazgos',

             'view_type': 'form',

             'view_mode': 'form',

             'res_model': 'mro.request',

#             'res_id': id[0],

             'target': 'current',

              'context':context,

        }



class mro_request(models.Model):
    _name = 'mro.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread']
#Todo: regresar a Claim
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('claim', 'Solicitada'),
        ('run', 'Execution'),
        ('done', 'Done'),
        ('reject', 'Rejected'),
        ('cancel', 'Canceled')
    ]

    ISSUE_LEVEL = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),

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
    name = fields.Char('Referencia', size=64)
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True,
         track_visibility='onchange', default='draft')


    issue_level = fields.Selection(ISSUE_LEVEL, 'Criticidad', required=True,
                             track_visibility='onchange', default='bajo')

    audit_type_id = fields.Many2one('mro.audit_type', 'Tipo Auditoria', required=True,
                                    states={'draft': [('readonly', False)]})
    audit_category_id = fields.Many2one('mro.audit_category', 'Categoria',
                                        required=True,
                                        states={'draft': [('readonly', False)]})
    audit_subcategory_id = fields.Many2one('mro.audit_subcategory', 'Subcategoria', required=True,
                                           states={'draft': [('readonly', False)]})
    audit_area_afectacion_id = fields.Many2one('mro.audit_area_afectacion', 'Afectación', required=True,
                                           states={'draft': [('readonly', False)]})

    audit_issue_id = fields.Many2one('mro.audit_issue', 'Hallazgos', required=True,
                                     states={'draft': [('readonly', False)]})
    asset_id = fields.Many2one('asset.asset', 'Activo', domain=[('category_id.name', '=', "Edificio")],
                               required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    cause = fields.Char('Cause', size=64, translate=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text('Descripción', required=True, readonly=True, states={'draft': [('readonly', False)]})
    reject_reason = fields.Text('Razón rechazo', readonly=True)
    requested_date = fields.Datetime('Fecha solicitud', required=True, readonly=True,
                                     states={'draft': [('readonly', False)]},
                                     help="Date requested by the customer for maintenance.",
                                     default=time.strftime('%Y-%m-%d %H:%M:%S'))
    execution_date = fields.Datetime('Fecha ejecución', required=True, readonly=True,
                                     states={'draft':[('readonly',False)],'claim':[('readonly',False)]},
                                     default=time.strftime('%Y-%m-%d %H:%M:%S'))
    breakdown = fields.Boolean('Breakdown', readonly=True, states={'draft': [('readonly', False)]}, default=False)
    create_user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self._uid)

    mro_audit_id = fields.Many2one('mro.audit', 'Auditoria')

    @api.onchange('audit_type_id')
    def onchange_audit_type_id(self):
        if self.audit_type_id:
            self.env.cr.execute(
                "Select distinct mro_audit_category_id from mro_audit_issue " +
                "   where mro_audit_type_id=" + str(self.audit_type_id.id))
            values =self.env.cr.dictfetchall()
            category_ids = []
            for res in values:
                category_ids.append(res['mro_audit_category_id'])
            if category_ids:
                print(category_ids)
                return {'domain': {'audit_category_id': [('id', 'in', category_ids)]}}
            else:
                return {'domain': {'audit_category_id': [('id', '=', -1)]}}
        else:
            return {'domain': {'audit_category_id': [('id', '=', -1)]}}

    @api.onchange('audit_category_id')
    def onchange_audit_category_id(self):
        print(self.audit_category_id)
        if self.audit_type_id and self.audit_category_id:
            self.env.cr.execute(
                "Select distinct mro_audit_subcategory_id from mro_audit_issue " +
                "   where mro_audit_type_id=" + str(self.audit_type_id.id) +
                "   and mro_audit_category_id=" + str(self.audit_category_id.id))
            values = self.env.cr.dictfetchall()
            subcategory_ids = []
            for res in values:
                subcategory_ids.append(res['mro_audit_subcategory_id'])
            if subcategory_ids:
                print(subcategory_ids)
                return {'domain': {'audit_subcategory_id': [('id', 'in', subcategory_ids)]}}
            else:
                return {'domain': {'audit_subcategory_id': [('id', '=', -1)]}}
        else:
            return {'domain': {'audit_subcategory_id': [('id', '=', -1)]}}

    @api.onchange('audit_subcategory_id')
    def onchange_audit_subcategory_id(self):
        print(self.audit_subcategory_id)
        if self.audit_type_id and self.audit_category_id and self.audit_subcategory_id:
            self.env.cr.execute(
                "Select distinct mro_audit_area_afectacion_id from mro_audit_issue " +
                "   where mro_audit_type_id=" + str(self.audit_type_id.id) +
                "   and mro_audit_category_id=" + str(self.audit_category_id.id) +
                "   and mro_audit_subcategory_id=" + str(self.audit_subcategory_id.id))
            values = self.env.cr.dictfetchall()
            afectacion_ids = []
            for res in values:
                afectacion_ids.append(res['mro_audit_area_afectacion_id'])
            if afectacion_ids:
                print(afectacion_ids)
                return {'domain': {'audit_area_afectacion_id': [('id', 'in', afectacion_ids)]}}
            else:
                return {'domain': {'audit_area_afectacion_id': [('id', '=', -1)]}}
        else:
            return {'domain': {'audit_area_afectacion_id': [('id', '=', -1)]}}


    @api.onchange('audit_area_afectacion_id')
    def onchange_audit_area_afectacion_id(self):

        if self.audit_type_id and self.audit_category_id \
                and self.audit_subcategory_id and self.audit_area_afectacion_id:
            issues = self.env['mro.audit_issue'].search(['&', ('mro_audit_type_id.id', '=', self.audit_type_id.id),
                                         ('mro_audit_category_id.id', '=', self.audit_category_id.id),
                                         ('mro_audit_subcategory_id.id', '=', self.audit_subcategory_id.id),
                                         ('mro_audit_area_afectacion_id.id', '=', self.audit_area_afectacion_id.id)])
            print('HALLAZGOS:', issues)
            listids = []
            readylistids = []
            if issues:
                for each in issues:
                    listids.append(each.id)
                print(listids)
                readylistids = list(dict.fromkeys(listids))
                print(readylistids)
            return {'domain': {'audit_issue_id': [('id', 'in', listids)]}}
        else:
            return {'domain': {'audit_issue_id': [('id', '=', -1)]}}

    @api.onchange('requested_date')
    def onchange_requested_date(self):
        self.execution_date = self.requested_date

    @api.onchange('execution_date','state')
    def onchange_execution_date(self):
        if self.state == 'draft':
            self.requested_date = self.execution_date

    def action_send(self):
        value = {'state': 'claim'}
        for request in self:
            if request.breakdown:
                value['requested_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
            request.write(value)

    def action_confirm(self):
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
                'description': request.description,
                'problem_description': request.description,
                'request_id': request.id,
            })
        self.write({'state': 'run'})
        return order_id.id

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

    def action_confirm(self):
        for order in self:
            order.write({'state': 'released'})
        return 0

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

