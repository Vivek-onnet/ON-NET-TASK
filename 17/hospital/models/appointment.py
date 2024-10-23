from odoo import models, fields, api
from datetime import date

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = 'mail.thread','mail.activity.mixin'
    _description = 'Hospital Management System'
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('hospital.patient', string="Patient Name")
    age = fields.Integer(related="patient_id.age",compute="_compute_age")
    gender = fields.Selection(related="patient_id.gender",readonly=False)
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now())
    booking_date = fields.Date(string="Booking Date", default=fields.Date.today())
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([('0', 'Normal'),
                                          ('1', 'Low'),
                                          ('2', 'High'),
                                          ('3', 'Very High')], string="Priority")
    state = fields.Selection([('draft', 'Draft'), ('in_consultation', 'In_Consultation'),  ('dones', 'Dones'), ('cancel', 'Cancel')], string="States")
    doctor_id = fields.Many2one('res.users', string="Doctor")
    pharmacy_id = fields.One2many('appointment.pharmacy', 'appointment_id', string="Pharmacy")
    hide_sale_price = fields.Boolean(string="Hide sale price")




    def object_test(self):
            print("test")
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Save Successfully..!!',
                    'type': 'rainbow_man',
                }
            }


    def action_is_consultation(self):
        for rec in self:
            rec.state = 'in_consultation'


    def action_done(self):
        for rec in self:
            rec.state = 'done'


    def action_cancel(self):
        action = self.env.ref('hospital.action_cancel_appointment').read()[0]
        return action


    def action_draft(self):
        for rec in self:
            rec.state = 'draft'


class AppointmentPharmacy(models.Model):
    _name = 'appointment.pharmacy'
    _description = 'Appointment Pharmacy'

    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Integer(string="Quantity")
    price = fields.Float(string="Price",related="product_id.list_price")
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")