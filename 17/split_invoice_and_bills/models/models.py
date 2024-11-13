from odoo import models, fields, api

class SplitBills(models.Model):
    _inherit = 'account.move'

    parent_invoice_id = fields.Many2one('account.move', string='Parent Invoice', store=True)
    split_invoice_count = fields.Integer(compute='_compute_split_invoice_count', string="Split Invoice")

    @api.depends('parent_invoice_id')
    def _compute_split_invoice_count(self):
        """Count the child invoices where the current record is the parent"""
        for record in self:
            record.split_invoice_count = self.env['account.move'].search_count([('parent_invoice_id', '=', record.id)])


    def action_split_bills_invoice_wizard(self):
        """Action to open the wizard for split invoice"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'split.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_cmr_ids': self.partner_id.id
            },
        }

    def action_view_split_invoices(self):
        """Action to open the tree view of split invoices"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('parent_invoice_id', '=', self.id)],
        }

