 #-*- coding: utf-8 -*-

from odoo import models, fields, api,_


class Requisition(models.Model):
     _name = 'material_requisition.requisition'
     _description ='Material requisition from manufactured order'

     name = fields.Char('Requisicion', required=True, copy=False, readonly=True,
                        index=True, default=lambda self: _('New'))

     user_id = fields.Many2one('res.users', string="Solicitante", required=True, default=lambda self: self.env.user )

     reason = fields.Text()

     @api.model
     def create(self, values):

        if values.get('name', _('New')) == _('New'):
             values['name'] = self.env['ir.sequence'].next_by_code('material_requisition.requisition_seq')
        return super(Requisition, self).create(values)

