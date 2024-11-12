from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class split_bills(models.Model):
    _inherit = 'account.move'

    split_invoice_ids = fields.One2many('account.move', 'parent_invoice_id', string='Split Invoices' , store=True)
    parent_invoice_id = fields.Many2one('account.move', string='Parent Invoice' , store=True)

    def action_split_bills_invoice_wizard(self):
        new_customer_ids = self.env['res.partner'].search([('id', '!=', self.partner_id.id),('customer_rank', '>', 0)],order='id')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'split.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_cmr_ids': new_customer_ids.ids
            },
        }

    has_split_invoices = fields.Boolean(compute='_compute_has_split_invoices', store=False)

    @api.depends('split_invoice_ids')
    def _compute_has_split_invoices(self):
        for record in self:
            record.has_split_invoices = bool(record.split_invoice_ids)

    has_parent_invoice_id = fields.Boolean(compute='_compute_has_parent_invoice_id', store=False)

    @api.depends('split_invoice_ids')
    def _compute_has_parent_invoice_id(self):
        for record in self:
            record.has_parent_invoice_id = bool(record.parent_invoice_id)

    def action_view_split_invoices(self):
        # action to open the tree view of split invoices
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('parent_invoice_id', '=', self.id)],
            'context': {'default_parent_invoice_id': self.id},
        }

