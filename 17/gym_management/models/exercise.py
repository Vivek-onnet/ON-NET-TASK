from odoo import models, fields, api
from datetime import timedelta


class Exercise(models.Model):
    _name = 'gym_management.exercise'

    name = fields.Char(string='Name')
    body_part = fields.Char(string='Body Part')
    equipment = fields.Char(string='Equipment')
    sets = fields.Integer(string='Sets')
    repeat = fields.Integer(string='Repeat')
    steps = fields.Html(string='Steps')
    benefits = fields.Html(string='Benefits')

