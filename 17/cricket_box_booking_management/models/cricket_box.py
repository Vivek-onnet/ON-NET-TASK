from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import re


class CricketBox(models.Model):
    """
        Model for managing Cricket Box details including name, duration,
        time slots, price, overview, currency, and status.
    """
    _name = 'cricket.box'
    _description = 'Cricket Box'

    name = fields.Char(string='Name', help='Name of the Cricket Box')
    box_poster = fields.Binary(string='Box Poster', help='Picture of Cricket Box')
    street = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State')
    email = fields.Char()
    phone = fields.Char()
    partner_id = fields.One2many('cricket.box.registration', 'box_id', string='Partner')
    select_dates = fields.One2many('all.date','box_id',string='Available dates')
    price = fields.Monetary(currency_field='currency_id', string='Price/Hour',
                            help='Mention the Pass price')
    about_cricket_box = fields.Text(string='About Cricket Box', help='Overview of the Cricket Box.')
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  help="Currency",
                                  required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([('draft', 'Draft'),
                              ('ongoing', 'Ongoing'),
                              ('cancel', 'Stop')],
                             string='Status', default='draft',)


    def action_start(self):
        """ Function for changing the state into ongoing."""
        self.write({'state': 'ongoing'})

    def action_reset(self):
        """ Function for changing the state into ongoing."""
        if self.state == 'cancel':
            self.write({'state': 'draft'})


    def action_cancel(self):
        """ Function for changing the state into cancel."""
        self.write({'state': 'cancel'})


    @api.constrains('email')
    def _check_email(self):
        """ Constraint for the Email, constraint will raise  validation error if the email is not valid"""
        email_regex = r'^[a-z0-9\.-]+@[a-z0-9\.-]+\.[a-z]{2,}$'

        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(_("Please enter a valid email address."))

    @api.constrains('phone')
    def _check_phone(self):
        """constraint will raise  validation error if the Phone number is not valid"""
        phone_regex = r'^[0-9]{10}$'
        for record in self:
            if record.phone and not re.match(phone_regex, record.phone):
                raise ValidationError(_("Please enter a valid Phone number."))



    def action_open_invoices(self):
        """ Function for viewing created invoices"""
        return {
            'name': 'Invoice',
            'domain': [('box_id', '=', self.id), ('move_type', '=', 'out_invoice',)],
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def action_open_credit_note(self):
        """ Function for viewing created Credit Note"""
        return {
            'name': 'Credit Note',
            'domain': [('box_id', '=', self.id), ('move_type', '=', 'out_refund',)],
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }