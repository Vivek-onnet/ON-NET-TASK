from odoo import api, fields, models

class StockMoveQty(models.Model):
    _inherit = 'stock.move'


    @api.depends('move_line_ids.quantity', 'move_line_ids.product_uom_id')
    def _compute_quantity(self):
        res = super(StockMoveQty, self)._compute_quantity()
        for move in self:
            if move.picking_type_id.code == 'incoming':
                move.quantity = 0

        return res
