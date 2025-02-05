from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # registration_id = fields.Many2one('account.move', string='Registration ID')

    admission_registration_id = fields.Many2one(
        'admission.registration',
        string='Admission Registration',
        help='Link to the Admission Registration')
    is_registration_invoice = fields.Boolean(string='Is registration Invoice')


