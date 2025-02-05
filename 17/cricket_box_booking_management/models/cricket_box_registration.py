from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError
import datetime
import pytz
from datetime import datetime, timedelta ,time


class CricketBoxRegistration(models.Model):
    """
        Model for managing Cricket Box registrations including details like partner,
        Cricket Box, date, time slot, pass, etc.
    """
    _name = 'cricket.box.registration'
    _description = 'Cricket Box Registration'

    name = fields.Char(required=True, copy=False,
                       default='New', readonly=True,
                       help='Name of the Ticket')
    active = fields.Boolean('Active')
    partner_id = fields.Many2one('res.partner', required=True, string='Select Partner', help='Mention the partner')
    box_id = fields.Many2one('cricket.box', string='Select Box', required=True, help='Mention the box id',
                             domain=[('state', '=', 'ongoing')])
    date = fields.Date(string='Date', default=fields.Date.today(), required=True, help='Mention the date for booking.')
    # time_slot_ids
    time_slot_id = fields.Many2many('time.slots', string='Select time slot',  required=True,
                                    domain="[('id', 'in', available_time_slots_ids)]",
                                     help='Mention the time slots of the Cricket Box')
    available_time_slots_ids = fields.Many2many('time.slots',
                                                string='Available time slots',
                                            compute='_compute_all_available_time_slots_ids',
                                                help='Mention the available time slots')
    box_price = fields.Monetary(string='box Price',  required=True,
                                related='box_id.price',
                                help='Price of the Box ticket')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  help="Currency",
                                  required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    no_of_tickets = fields.Integer(string='Number of Slots', default=1,
                                   help='Mention the number of tickets')
    total_price = fields.Integer(string='Total Price',
                                 compute='_compute_total_price',
                                 default=0)
    refund = fields.Integer(string='Total Refund',
                            default=0)
    box_poster = fields.Binary(related='box_id.box_poster',
                               string='Box Wallpapers',
                               help='Wallpapers of the Cricket Box.')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('invoiced', 'Invoiced'),
                              ('canceled', 'Canceled'),
                              ], string='Status',
                             default='draft', help='Status of the Box registration')

    @api.constrains('date')
    def _check_date(self):
        """ Constraint for the date, constraint will raise  validation error if the date is in the past"""
        today = fields.Date.today()
        for rec in self:
            if rec.date < today:
                raise ValidationError('Date cannot be in the PAST!!!')

    def action_submit(self):
        """ Function for writing the state into done."""
        self.write({'state': 'done'})
        return {
            'effect': {'fadeout': 'slow',
                       'message': 'Your Sloat is Book..! Please Payment Now!!!',
                       'type': 'rainbow_man'}
        }

    def action_invoice(self):
        """ Function for creating invoice."""
        product_id = self.env.ref('cricket_box_booking_management.product_1')
        try:
            val = [{
                'move_type': 'out_invoice',
                'partner_id': self.partner_id.id,
                'is_booking_invoice': True,
                'box_ticket_id': self.id,
                'box_id': self.box_id.id,
                'date': self.date,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [
                    (0, 0,
                     {
                         'product_id': product_id.id,
                         'name': product_id.name,
                         'quantity': self.no_of_tickets,
                         'price_unit': self.box_id.price,
                     })],
            }]
            move = self.env['account.move'].create(val)
            self.write({'state': 'invoiced'})
            move.action_post()
            re = {
                'name': 'Invoice',
                'res_id': move.id,
                'res_model': 'account.move',
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
            }
            return re
        except:
            raise ValidationError('Invoice Creation Failed!')

    def action_show(self):
        """ Function for changing the state into ongoing."""
        if self.state == 'invoiced' or self.state == 'canceled':
            self.write({'state': 'done'})

    @api.depends('box_id', 'date', 'time_slot_id','available_time_slots_ids')
    def _compute_all_available_time_slots_ids(self):
        for rec in self:
            rec.available_time_slots_ids = [(5, 0, 0)]
            all_slots = self.env['all.date'].search([])
            for slot in all_slots:
                if rec.box_id and slot.box_id == rec.box_id and slot.date == rec.date:
                    rec.available_time_slots_ids = slot.available_time_slots_ids
            rec.no_of_tickets = (len(rec.time_slot_id.ids))
            today = fields.Date.today()
            if rec.date:
                rec.active = True
            if rec.date and rec.date < today:
                rec.active = False

    @api.model
    def create(self, vals):
        """ Function for create sequence of records"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cricket.box.registration')
        res = super(CricketBoxRegistration, self).create(vals)
        return res


    @api.depends('box_id', 'date')
    def _compute_total_price(self):
        for record in self:
            if record.no_of_tickets and  record.no_of_tickets > 0:
                record.total_price = record.no_of_tickets * record.box_price
                moves = self.env['account.move'].search([('box_ticket_id', '=', self.id), ('move_type', '=', 'out_refund')])
                for move in moves:
                    record.refund = abs(move.amount_total_signed)
                    break


    def action_open_invoices(self):
        """ Function for viewing created invoices"""
        return {
            'name': 'Invoice',
            'domain': [('box_ticket_id', '=', self.id), ('move_type', '=', 'out_invoice',)],
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def action_open_credit_note(self):
        """ Function for viewing created Credit Note"""
        return {
            'name': 'Credit Note',
            'domain': [('box_ticket_id', '=', self.id), ('move_type', '=', 'out_refund',)],
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


    @api.onchange('box_id', 'date')
    def _onchange_set_values(self):
        for record in self:
            record.update({'time_slot_id': None})
            record.total_price = record.no_of_tickets * record.box_price


    def action_refund_and_cancel(self):
        """
        function for refundable cancelletion of a booking.
        refund based on the remaining time to the booking date:
        - >48 hours: 100% refund
        - >24 hours: 50% refund
        - >12 hours: 20% refund
        - <12 hours: No refund
        """
        product_id = self.env.ref('cricket_box_booking_management.product_1')
        for record in self:
            if record.state == 'invoiced':
                for slot in record.time_slot_id:
                    if not slot.time:
                        continue
                    # calculate time diffarence
                    user_tz = pytz.timezone(self.env.user.tz)
                    now = datetime.now(user_tz)

                    slot_start = datetime.combine(record.date, time(int(slot.time), int((slot.time - int(slot.time)) * 60)))
                    time_difference = slot_start - now.replace(tzinfo=None)

                    hours_left = time_difference.total_seconds() / 3600
                    if hours_left > 48:
                        refund_percentage = 100
                    elif hours_left > 24:
                        refund_percentage = 50
                    elif hours_left > 12:
                        refund_percentage = 20
                    elif hours_left > 6:
                        refund_percentage = 10
                    else:
                        refund_percentage = 0
                    print("hours_left:",hours_left)
                    print("refund_percentage:",refund_percentage)
                    if refund_percentage > 1:
                        # calculate refund
                        refund_amount = record.box_id.price * (refund_percentage / 100)

                        # create a credit note with negative refund amount
                        refund_vals = {
                            'move_type': 'out_refund',
                            'partner_id': self.partner_id.id,
                            'is_booking_invoice': True,
                            'box_ticket_id': self.id,
                            'box_id': self.box_id.id,
                            'invoice_date': fields.Date.today(),
                            'invoice_line_ids': [
                                (0, 0, {
                                    'product_id': product_id.id,
                                    'name': product_id.name,
                                    'quantity': self.no_of_tickets,
                                    'price_unit': refund_amount,
                                }),
                            ],
                        }
                        refund_move = self.env['account.move'].create(refund_vals)

                        if refund_move.amount_total < 0:
                            raise ValidationError("Cannot create a credit note with a negative total amount.")

                        # post the credit note
                        refund_move.action_post()

                        # update state to canceled
                        record.state = 'canceled'

                        return {
                            'domain': [('id', 'in', refund_move.ids)],
                            'name': 'Credit Note',
                            'res_model': 'account.move',
                            'view_id': False,
                            'view_mode': 'tree,form',
                            'type': 'ir.actions.act_window',
                        }
                    elif refund_percentage <= 1:
                        raise UserError(_("Cannot cancel a booking because it's too close to the Slot time."))
                        # self.action_cancel_without_refund()


            else:
                raise ValidationError(_("Cannot cancel a booking that hasn't been invoiced."))

    def action_cancel_without_refund(self):
        """
        Cancel the booking without issuing a refund.
        """
        for record in self:
            if record.state in ['draft', 'done']:
            # if record.state:
                record.state = 'canceled'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Booking canceled without a refund.',
                        'type': 'rainbow_man',
                    }
                }
            else:
                raise ValidationError("Cannot cancel a booking that has already been invoiced or refunded.")

    def action_generate_pass_pdf(self):
        """ Function for downloading pass pdf."""
        return self.env.ref('cricket_box_booking_management.action_report_cricket_box_pass').report_action(self)
