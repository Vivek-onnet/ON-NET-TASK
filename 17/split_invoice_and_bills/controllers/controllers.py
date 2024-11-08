# -*- coding: utf-8 -*-
# from odoo import http


# class SplitBills(http.Controller):
#     @http.route('/split_bills/split_bills', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/split_bills/split_bills/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('split_bills.listing', {
#             'root': '/split_bills/split_bills',
#             'objects': http.request.env['split_bills.split_bills'].search([]),
#         })

#     @http.route('/split_bills/split_bills/objects/<model("split_bills.split_bills"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('split_bills.object', {
#             'object': obj
#         })

