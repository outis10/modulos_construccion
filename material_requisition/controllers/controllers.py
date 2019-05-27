# -*- coding: utf-8 -*-
from odoo import http

# class MaterialRequisition(http.Controller):
#     @http.route('/material_requisition/material_requisition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/material_requisition/material_requisition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('material_requisition.listing', {
#             'root': '/material_requisition/material_requisition',
#             'objects': http.request.env['material_requisition.material_requisition'].search([]),
#         })

#     @http.route('/material_requisition/material_requisition/objects/<model("material_requisition.material_requisition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('material_requisition.object', {
#             'object': obj
#         })