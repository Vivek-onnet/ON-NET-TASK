from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class split_bills(models.Model):
    _inherit = 'account.move'

    split_invoice_ids = fields.One2many('account.move', 'parent_invoice_id', string='Split Invoices' , store=True)
    parent_invoice_id = fields.Many2one('account.move', string='Parent Invoice' , store=True)

    def action_split_bills_invoice_wizard(self):
        # Get the view ID for the wizard
        view = self.env['ir.actions.act_window']._for_xml_id('split_bills.action_split_bills_invoice_wizard')
        view['context'] = {'default_partner_id': self.partner_id.id, 'active_id': self.id, }
        return view

    has_split_invoices = fields.Boolean(compute='_compute_has_split_invoices'  ,store=False)

    @api.depends('split_invoice_ids')
    def _compute_has_split_invoices(self):
        for record in self:
            record.has_split_invoices = bool(record.split_invoice_ids)

    has_parent_invoice_id = fields.Boolean(compute='_compute_has_parent_invoice_id'  ,store=False)

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

    # def action_open_parent_invoice(self):
    #     # action to open the invoice view of parent invoices
    #     if not self.parent_invoice_id.id == False:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'account.move',
    #             'view_mode': 'form',
    #             'res_id': self.parent_invoice_id.id,
    #             'target': 'current',
    #         }
    #     else:
    #         # if p.in not thn error
    #         raise ValidationError(_("This is Parent Invoice"))


# class inherit_crm_lead(models.Model):
#     _inherit = 'crm.lead'
#
#     @api.model
#     def default_get(self, fields):
#         result = super(inherit_crm_lead, self).default_get(fields)
#         result['name'] = 'vivek'
#         return result
#
#     @api.onchange('partner_id')
#     def _onchange_partner_id(self):
#         if self.partner_id:
#             self.name = self.partner_id.name + " vivek"