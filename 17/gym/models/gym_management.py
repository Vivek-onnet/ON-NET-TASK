from odoo import api, exceptions, fields, models
from datetime import timedelta, date
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re


class GymManagement(models.Model):
    _name = "gym.management"
    _description = 'Gym Management'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True, index=True,string='Related Partner', help='Partner-related data of the user')

    gymid = fields.Char(string='Gym ID', readonly=True)
    # name = fields.Char(string='Name', required=True)
    bdate = fields.Date(string="Birth Date", required=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    gym = fields.Boolean(string='Active User')
    weight = fields.Float(string='Weight (kg)', required=True)
    height = fields.Float(string='Height (cm)', required=True, digits=(4, 2))
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    health_status = fields.Char(string='Health Status', compute='_compute_health_status', store=True)
    member_workout_ids = fields.One2many('member_workout', 'members_id', string='Workout Plans')
    attendance_ids = fields.One2many('hr.attendance', 'name', string='Attendance Records')
    member_diet_ids = fields.One2many('member_diet', 'member_id', string='Diet Plans')
    company_type = fields.Selection([('person', 'Member'),('company', 'Trainer')], default='person', store=True)

    @api.model
    def _change_id_with_para(self, add_string):
        """Function call from XML WITH parameters ,this method is used to add roll number//ID to the Gym profile"""
        records = self.search([('is_company', '=', False)])
        for record in records:
            record.gymid = add_string + "GMID" + str(record.id)

        records = self.search([('is_company', '=', True)])
        for record in records:
            record.gymid = add_string + "TID" + str(record.id)

    @api.constrains('bdate')
    def _check_bdate(self):
        """Constraint for the Birth Date,constraint will raise  validation error if the selected birth date is in the future"""
        for record in self:
            if record.bdate and record.bdate >= date.today():
                raise ValidationError(_("Birth Date must be in the past."))

    ## used to automate calculations and derive values based on predefined functions , ensuring data accuracy and reducing manual effort.
    ## age = fields.Integer(compute='_compute_age', string="Age", store=True) #  store = True attributes is used to STORE the field record in the DATABASE
    @api.depends('bdate')
    def _compute_age(self):
        """Computed Fields for Age// Date """
        for rec in self:
            if rec.bdate:
                rec.age = (fields.Date.today() - rec.bdate).days // 365
            else:
                rec.age = 0

    @api.depends('bmi')
    def _compute_health_status(self):
        """Computed Fields for Health Status and BMI"""
        for record in self:
            if record.bmi < 18.5:
                record.health_status = 'Underweight'
            elif 18.5 <= record.bmi < 24.9:
                record.health_status = 'Healthy'
            elif 25 <= record.bmi < 29.9:
                record.health_status = 'Overweight'
            else:
                record.health_status = 'Obese'

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        """Constraint for the Start Date"""
        for record in self:
            if record.height > 0:  # Check if height is valid
                height_in_meters = record.height / 100.0
                record.bmi = record.weight / (height_in_meters ** 2)
            else:
                record.bmi = 0.0  # Set BMI to 0 if height is invalid

    @api.depends('name')
    def _compute_display_name(self):
        """Computed Fields for Display name """
        for record in self:
            record.display_name = record.name

    @api.onchange('bdate')
    def _compute_gym(self):
        for record in self:
            if record.bdate:
                record.gym = True
            else:
                record.gym = False

    @api.constrains('email')
    def _check_email(self):
        """ Constraint for the Email, constraint will raise  validation error if the email is not valid"""
        email_regex = r'^[a-z0-9\.-]+@[a-z0-9\.-]+\.[a-z]{2,}$'

        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(_("Please enter a valid email address."))

    # constraint will raise  validation error if the Phone number is not valid
    @api.constrains('phone')
    def _check_phone(self):
        """ Constraint for the Phone number"""
        phone_regex = r'^[0-9]{10}$'

        for record in self:
            if record.phone and not re.match(phone_regex, record.phone):
                raise ValidationError(_("Please enter a valid Phone number."))