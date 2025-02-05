from odoo import api, fields, models
from collections import defaultdict



class StockMoveQty(models.Model):
    _inherit = 'stock.move'


    @api.depends('move_line_ids.quantity', 'move_line_ids.product_uom_id')
    def _compute_quantity(self):
        print("hii")
        res = super(StockMoveQty, self)._compute_quantity()
        for move in self:
            if move.picking_type_id.code == 'incoming':
                print("move.picking_type_id.code",move.picking_type_id.code)
                move.quantity = 0
                print("120120MOVE",move.quantity)


        return res
