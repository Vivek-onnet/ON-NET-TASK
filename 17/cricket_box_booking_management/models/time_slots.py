from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import datetime #///////
import pytz
from datetime import datetime, timedelta, time



class TimeSlots(models.Model):
    _name = 'time.slots'
    _description = 'Time Slots'

    name = fields.Char(string='Time Slot', default='New',
                       readonly=True, help='Mention the name of the Time slots')
    time = fields.Float(string='Box Time', help='Mention the slot time')
    color = fields.Integer(string='Color Index', default=10)


    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Name should be unique")
    ]

    @staticmethod
    def _format_time(hour):
        """helper method to format float hours into 12-hour time with AM/PM."""
        hours, minutes = divmod(hour * 60, 60)
        time_obj = datetime.strptime(f'{int(hours)}:{int(minutes)}', "%H:%M")
        return time_obj.strftime("%I:%M %p")

    @api.model
    def create(self, vals):
        """ create function to update name."""
        if vals['time']:
            vals['name'] = self._format_time(vals['time'])
        else:
            raise ValidationError('Please mention time!!')
        return super().create(vals)

    @api.model
    def write(self, vals):
        """ write function to update name."""
        if vals['time']:
            vals['name'] = self._format_time(vals['time'])
        res = super(TimeSlots, self).write(vals)
        return res



class AllDate(models.Model):
    _name = 'all.date'
    _description = 'All Date'
    _rec_name = 'date'

    date = fields.Date(string='Dates', help='Mention the date')
    time_slot_ids = fields.Many2many('time.slots','all_book_slot_rel_table', 'box_col', 'slot_col',
                                    string='Select time slot', help='Mention the time slots of the Cricket Box')
    available_time_slots_ids = fields.Many2many('time.slots',
                                                string='Available Time Slots',
                                                help='Time slots of the Cricket Box availability')
    booked_time_slots_ids = fields.Many2many('time.slots', 'book_slot_rel_table', 'box_col', 'slot_col',
                                             string='Booked Time Slots',
                                             help='Time slots of  Booked Cricket Box',compute="_compute_time_slots",)
    box_id = fields.Many2one('cricket.box', string='Box Name',required=True)
    active = fields.Boolean('Active')
    datetime_start = fields.Datetime(string='Start DateTime', help='Start datetime for calendar')
    datetime_end = fields.Datetime(string='End DateTime', help='End datetime for calendar')



    @api.constrains('date')
    def _check_date(self):
        """ Constraint for the date, constraint will raise  validation error if the date is in the past"""
        today = fields.Date.today()
        for rec in self:
            if rec.date < today:
                raise ValidationError('Date cannot be in the PAST!!!')


    @api.depends('date', 'box_id', 'booked_time_slots_ids', 'box_id.partner_id')
    def _compute_time_slots(self):
        """
        Compute available and booked time slots based on the partner's selected time slots and the check date.
        """
        today = fields.Date.today()
        user_tz = pytz.timezone(self.env.user.tz)

        for record in self:
            # fetch all time slots
            time_slot_id = self.env['time.slots'].search([]).ids
            record.time_slot_ids = [(6, 0, time_slot_id)]
            record.available_time_slots_ids = [(6, 0, time_slot_id)]
            record.booked_time_slots_ids = [(5, 0, 0)]

            if record.date and record.date >= today:
                record.active = True
                for rec in record.box_id.partner_id:
                    if rec.date and rec.date < today:
                        rec.active = False
            else:
                record.active = False
                continue
            # first check box_id and partner_id are set
            booked_slots = self.env['time.slots']
            if record.box_id and record.box_id.partner_id:
                for partner_record in record.box_id.partner_id:
                    if partner_record.state != 'canceled' and partner_record.date == record.date:
                          # add partner's booked slots to the list
                        booked_slots |= partner_record.time_slot_id

                # update booked_time_slots_ids
                record.booked_time_slots_ids = [(6, 0, booked_slots.ids)]

            now = datetime.now(user_tz).replace(tzinfo=None)
            for slot in record.time_slot_ids:
                if not slot.time:
                    continue
                slot_start = datetime.combine(record.date,time(int(slot.time), int((slot.time - int(slot.time)) * 60)))
                slot_start_local = user_tz.localize(slot_start)
                slot_start_utc = slot_start_local.astimezone(user_tz).replace(tzinfo=None)
                if now > slot_start_utc:
                    booked_slots |= slot
                # a = set(booked_slots.ids)
                record.booked_time_slots_ids = [(6, 0, booked_slots.ids)]

                available_slots = self.env['time.slots']
                # compute available slots by subtracting booked slots
                available = self.env['time.slots'].browse(time_slot_id) - booked_slots
                available_slots |= available

                a = booked_slots - available_slots
                record.booked_time_slots_ids = [(6, 0, a.ids)]

                record.available_time_slots_ids = [(6, 0, available_slots.ids)]


    def action_reg_box(self):
        """action for open registration form"""
        if self.box_id.state == 'ongoing':
            return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cricket.box.registration',
            'target':  'current',
            'context': {
                'default_box_id': self.box_id.id,
                'default_date': self.date,
            }
        }
        else:
            raise ValidationError(_('The service of this cricket box is closed temporarily!!'))

