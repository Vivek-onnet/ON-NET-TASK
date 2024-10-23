from odoo import models, fields, api

class PatientTag(models.Model):
    _name = 'patient.tag'
    _description = 'Patient Tag'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    color_picker = fields.Integer(string="Color Picker", default=3)
    color = fields.Char(string="Color Description", default="red")
