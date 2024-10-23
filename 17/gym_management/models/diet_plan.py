from odoo import models, fields


class Diet(models.Model):
    _name = 'gym_management.diet'

    name = fields.Char(string='Diet Food')
    quantity = fields.Char(string='Quantity')
    time = fields.Selection(selection=[('morning', 'Morning : 7 am '), ('afternoon', 'Afternoon : 12 pm '),
                                       ('evening', 'Evening : 5 pm'), ('night', 'Night : 8 pm')] ,string='Consume at')
    diet_id = fields.Many2one('gym_management.diet_plan',string=' ')

class DietPlan(models.Model):
    _name = 'gym_management.diet_plan'

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')
    diet_plan_id = fields.One2many('gym_management.diet', 'diet_id',string=' ')


class MemberDiet(models.Model):
    _name = 'gym_management.member_diet'

    member_id = fields.Many2one('res.partner', string='Member', required=True)
    diet_ids = fields.Many2one('gym_management.diet_plan', string='Diet Plan', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)