from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class CancelInvoiceWizard(models.TransientModel):
    _name = 'cancel.invoice.wizard'
    _description = 'Wizard to cancel specific invoices'

    partner_id = fields.Many2one('res.partner', string='Member',
                                 domain="[('member_lines.state', 'in', ['invoiced', 'paid','free', 'none', 'waiting', 'old'])]")

    selected_member_lines = fields.Many2many('membership.membership_line', string='Select Memberships',
                                             domain="[('state', 'in', ['invoiced', 'paid', 'free', 'old', 'none', 'waiting'])]")





    # def con(self):
    #    print (self.selected_member_lines.account_invoice_id.amount_untaxed_signed)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Filter selected_member_lines based on the current partner_id
            member_lines = self.partner_id.member_lines.filtered(
                lambda line: line.state in ['free', 'invoiced', 'paid', 'waiting','none'] and line.account_invoice_id.payment_state != 'reversed')
            unique_invoices = set()
            unique_member_lines = self.env['membership.membership_line']

            for line in member_lines:
                if line.account_invoice_id.id not in unique_invoices:
                    unique_invoices.add(line.account_invoice_id.id)
                    unique_member_lines |= line
            self.selected_member_lines = unique_member_lines



    def action_cancel_selected_invoices(self):
        for wizard in self:
            for line in wizard.selected_member_lines:
                # if line.account_invoice_id and line.state in ['free', 'invoiced', 'paid', 'old', 'none', 'waiting']:
                if line.account_invoice_id and line.state in ['free', 'invoiced', 'paid', 'waiting']:
                    invoice = line.account_invoice_id
                    if invoice.state != 'draft':
                        invoice.button_draft()
                    invoice.button_cancel()

    def action_payment_selected_invoices(self):
        for wizard in self:
            for line in wizard.selected_member_lines:
                if line.state in ['free', 'invoiced', 'waiting'] and line.account_invoice_id:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Process Payment',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'res_id': line.account_invoice_id.id,
                        'target': 'current',
                    }
            # Check for already paid lines
            has_pay_line = any(line.state == 'paid' for line in wizard.selected_member_lines)
            if has_pay_line:
                raise AccessError(_('Already Paid.'))
