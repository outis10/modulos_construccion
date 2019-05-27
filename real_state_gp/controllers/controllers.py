# -*- coding: utf-8 -*-
from odoo import http

# class RealStateGp(http.Controller):
#     @http.route('/real_state_gp/real_state_gp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_state_gp/real_state_gp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_state_gp.listing', {
#             'root': '/real_state_gp/real_state_gp',
#             'objects': http.request.env['real_state_gp.real_state_gp'].search([]),
#         })

#     @http.route('/real_state_gp/real_state_gp/objects/<model("real_state_gp.real_state_gp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_state_gp.object', {
#             'object': obj
#         })