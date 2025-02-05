from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_notification = fields.Boolean(string="Enable Email Notification",
                                        config_parameter='account.email_notification')

    notification_days = fields.Integer(
        string="Days for Notification",
        config_parameter='account.notification_days',
        required=True
    )

class ResPartner(models.Model):
    _inherit = 'res.partner'

    skip_email_reminder = fields.Boolean(
        string="Skip Email Reminder",
        help="If checked, this customer will not receive overdue payment reminders."
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _send_due_date_notifications(self):
        # get system configuretion
        config_params = self.env['ir.config_parameter'].sudo()
        email_notification_enabled = config_params.get_param('account.email_notification', default=False)
        notification_days = config_params.get_param('account.notification_days', default=0)

        if not email_notification_enabled or not notification_days:
            return

        notification_days = int(notification_days)
        today = fields.Date.today()

        # get all  invoices that are overdue
        invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('partner_id.skip_email_reminder', '=', False),

        ])

        for invoice in invoices:
            if invoice.invoice_date_due:
                print("invoice_date_due",invoice.invoice_date_due,notification_days)
                overdue_days = (today - invoice.invoice_date_due).days
                if overdue_days >= notification_days:
                    # send email notification
                    template = self.env.ref('email_notification_configuration.email_template_due_notification',raise_if_not_found=False)
                    if template:
                        template.send_mail(invoice.id, force_send=True)
                        print(f"Email sent for Invoice ID: {invoice.name},{invoice.partner_id.name} with {overdue_days} overdue days.")



