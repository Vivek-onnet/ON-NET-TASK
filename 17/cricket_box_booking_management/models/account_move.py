from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    box_ticket_id = fields.Many2one('account.move'
                                    ,string='Ticket ID')
    box_id = fields.Many2one('cricket.box', string='Box ID')
    is_booking_invoice = fields.Boolean(string='Is Box Invoice')


