from odoo import models, fields

class Days(models.Model):
    _name = 'days'

    name = fields.Char(string='Day', required=True)

class WorkoutPlan(models.Model):
    _name = 'workout_plan'

    name = fields.Char(string='Name', required=True)
    description = fields.Html(string='Description')
    workout_days_id = fields.Many2many('exercise','exercise_workout_plan_rel','exercise_id','workout_plan_id',string=' ')
    diet_plan_id = fields.One2many('diet', 'diet_ids',string=' ')

    w_days_id = fields.Many2many(
        'days',
        'days_workout_plan_rel',
        'workout_plan_id',
        'days_id',
        string='Workout Days'
    )



class MemberWorkout(models.Model):
    _name = 'member_workout'

    members_id = fields.Many2one('res.partner', string='Member', required=True)
    workout_id = fields.Many2one('workout_plan', string='Workout Plan', required=True)
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    #here we use releted function for use "days" field
    workout_days = fields.Many2many(related='workout_id.w_days_id', string='Workout Days')
