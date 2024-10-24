from odoo import models, fields, api,_
from datetime import timedelta

class GymInvoices(models.Model):
    _inherit = 'account.move'

    gym = fields.Boolean(string='Gym', default=True ,invisible=True)
    invoice_partner_display_name = fields.Char(compute='_compute_invoice_partner_display_info', store=True ,string='Name')
    for_gym = fields.Boolean(string='Gym', default=True, invisible=True)



    @api.depends('name')
    def _compute_invoice_partner_display_info(self):
        for record in self:
            # print(record.partner_id,record.partner_id.name,record.invoice_partner_display_name)
            record.invoice_partner_display_name = record.partner_id.name
            # print(record.invoice_partner_display_name)


