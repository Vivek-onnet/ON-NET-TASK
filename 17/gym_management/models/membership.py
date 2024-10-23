from odoo import models, fields, api
from datetime import timedelta

class Membership(models.Model):
    _inherit = 'product.template'

    name = fields.Char(string='Name', required=False)
    duration_months = fields.Integer(string='Months')
    membership = fields.Boolean(string='Active Membership')
    personal_trainer = fields.Boolean(string='Personal Trainer')
    types = fields.Selection([('membership', 'Membership'), ('personal_trainer', 'Personal Trainer')], string='Type')
    trainer_id = fields.Many2one('res.partner',domain="[('company_type', '=', 'company')]", string="Trainer")

    member_ids = fields.One2many(
        'res.partner', 'membership_id',
        compute='_compute_member_ids',
        string='Connected Members'
    )

    @api.depends('membership')
    def _compute_member_ids(self):
        for product in self:
            # Get the list of members related to this product template (membership)
            member_ids = self.env['res.partner'].search([('memberships_id', 'in', product.ids)])
            product.member_ids = member_ids


