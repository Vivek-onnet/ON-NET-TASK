from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = 'mail.thread','mail.activity.mixin'          ## "mail.thread" = for email, "mail.activity.mixin" = for activity tracking
    _description = 'Hospital Management System'

    name = fields.Char(string="Name",tracking=True)
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age")

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True)
    address = fields.Text(string="Address",tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    active = fields.Boolean(string="Archive", default=True)
    appointment_id = fields.Many2one('hospital.appointment', string="Patient ")
    image = fields.Image(string="Image" )
    tag_id = fields.Many2many('patient.tag', string="Tags")


    ### 2 Type of Constraints : both used for validation
    #1. SQL Constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Patient names must be unique!')
        ]

    #2. Python Constraints
    @api.constrains('date_of_birth')
    def _check_age(self):
        for rec in self:
            if rec.date_of_birth:
                if rec.date_of_birth > date.today():
                    raise ValidationError("Date of Birth cannot be in the future!")






    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0





















