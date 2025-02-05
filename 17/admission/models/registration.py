# from odoo import api, fields, models,_
# from odoo.exceptions import ValidationError
#
# class Subject(models.Model):
#     _name = 'admission.subject'
#     _description = 'Subject'
#
#     name = fields.Char(string="Subject Name", required=True)
#
# class registration(models.Model):
#     _name = 'registration'
#     _description = 'Registration'
#
#     name = fields.Char(string='Student name', required=True)
#     date_of_birth = fields.Date(string='Date of Birth', required=True)
#     age = fields.Integer(string='Age', compute='_compute_age')
#     medium = fields.Selection(string='Medium', required=True , selection=[('English', 'English'), ('Hindi', 'Hindi'), ('Gujarati', 'Gujarati')])
#     standard = fields.Selection(string='Standard ', required=True, selection=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8')])
#     # 	Subject (On selection of standard this subject field automatically populate all subject that is configured in standard),
#     # 	Teachers (On selection of standard this teachers field automatically populate all teachers that is configured in standard)
#     status = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'),('confirm', 'Confirm'), ('reject ', 'Reject ')], string='Status', default='draft')
#
#     @api.constrains('date_of_birth')
#     def _check_age(self):
#         for rec in self:
#             if rec.date_of_birth:
#                 if rec.date_of_birth > fields.Date.today():
#                     raise ValidationError(_("Date of birth should be in the past"))
#
#     @api.depends('date_of_birth')
#     def _compute_age(self):
#         for rec in self:
#             if rec.date_of_birth:
#                 rec.age = (fields.Date.today() - rec.date_of_birth).days // 365
#             else:
#                 rec.age = 0
#
#
#
#     def action_in_progress(self):
#         if self.name:
#             self.write({'status': 'in_progress'})
#
#     def action_confirm(self):
#         """Confirm - (button will be visible only in progress status)
#         on click of button need to create invoice of current record
#         and move status to Confirm , """
#         # if self.name:
#         # def action_invoice(self):
#         # """ Function for creating invoice."""
#         product_id = self.env.ref('admission.fees_product_1')
#         try:
#             val = [{
#                 'move_type': 'out_invoice',
#                 'partner_id': self.env.user,
#                 'is_registration_invoice': True,
#                 'registration_id': self.id,
#                 'date': self.date,
#                 'invoice_date': fields.Date.today(),
#                 'invoice_line_ids': [
#                     (0, 0,
#                      {
#                          'product_id': product_id.id,
#                          'name': product_id.name,
#                          'quantity': 1,
#                          'price_unit': 1000,
#                      })],
#             }]
#             move = self.env['account.move'].create(val)
#             self.write({'status': 'confirm'})
#             move.action_post()
#             re = {
#                 'name': 'Invoice',
#                 'res_id': move.id,
#                 'res_model': 'account.move',
#                 'view_id': False,
#                 'view_mode': 'form',
#                 'type': 'ir.actions.act_window',
#             }
#             return re
#         except:
#             raise ValidationError('Invoice Creation Failed!')
#
#     def action_reject(self):
#         """ Button will be visible only in progress status) on click of button need to popup wizard,
#         wizard will contain one text field name Reject reason and it’s required field.
#         After fill reason click on reject button record status will change to reject status and reject reason should be display in Chatter of record"""
#         self.write({'status': 'reject'})
#
#
#     def action_open_invoices(self):
#         """ Function for viewing created invoices"""
#         return {
#             'name': 'Invoice',
#             'domain': [('registration_id', '=', self.id), ('move_type', '=', 'out_invoice',)],
#             'res_model': 'account.move',
#             'view_id': False,
#             'view_mode': 'tree,form',
#             'type': 'ir.actions.act_window',
#         }

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Subject(models.Model):
    _name = 'admission.subject'
    _description = 'Subject'

    name = fields.Char(string="Subject Name", required=True)


class StandardSubjectLine(models.Model):
    _name = 'admission.standard.subject.line'
    _description = 'Standard Subject Line'

    subject_id = fields.Many2one('admission.subject', string="Subject", required=True)
    teacher_ids = fields.Many2many('res.partner', string="Teachers", domain="[('is_teacher', '=', True)]")


class Standard(models.Model):
    _name = 'admission.standard'
    _description = 'Standard'

    name = fields.Char(string="Standard Name", required=True)
    medium = fields.Selection([
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('gujarati', 'Gujarati')
    ], string="Medium", required=True)
    subject_line_ids = fields.One2many('admission.standard.subject.line', 'id', string="Subjects and Teachers")


class RegistrationFeeLine(models.Model):
    _name = 'admission.registration.fee.line'
    _description = 'Registration Fee Line'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1)
    tax_id = fields.Many2many('account.tax', string="Taxes")
    untaxed_amount = fields.Float(string="Untaxed Amount", compute="_compute_amounts")
    total_amount = fields.Float(string="Total Amount", compute="_compute_amounts")

    @api.depends('product_id', 'quantity', 'tax_id')
    def _compute_amounts(self):
        for line in self:
            price = line.product_id.lst_price * line.quantity
            taxes = line.tax_id.compute_all(price, currency=line.product_id.currency_id)
            line.untaxed_amount = taxes['total_excluded']
            line.total_amount = taxes['total_included']


class Registration(models.Model):
    _name = 'admission.registration'
    _description = 'Student Registration'

    name = fields.Char(string="Student Name", required=True)
    age = fields.Integer(string="Student Age", compute="_compute_age", store=True)
    date_of_birth = fields.Date(string="Date of Birth")
    medium = fields.Selection([
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('gujarati', 'Gujarati')
    ], string="Medium", required=True)
    standard_id = fields.Many2one('admission.standard', string="Standard", required=True)
    subject_ids = fields.Many2many('admission.subject', string="Subjects")
    teacher_ids = fields.Many2many('res.partner', string="Teachers")
    fee_line_ids = fields.One2many('admission.registration.fee.line', 'id', string="Fees")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ], string="Status", default='draft', required=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                rec.age = (fields.Date.today() - rec.date_of_birth).days // 365
            else:
                rec.age = 0

    def action_start(self):
        self.state = 'in_progress'

    def action_confirm(self):
        self.ensure_one()
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env.user.partner_id.id,
            'admission_registration_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.product_id.lst_price,
            }) for line in self.fee_line_ids]
        })
        self.state = 'confirmed'

    def action_reject(self):
        return {
            'name': _('Reject Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'admission.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_admission_registration_id': self.id}
        }


class RejectionWizard(models.TransientModel):
    _name = 'admission.rejection.wizard'
    _description = 'Rejection Wizard'

    reject_reason = fields.Text(string="Reject Reason", required=True)
    registration_id = fields.Many2one('admission.registration', string="Registration")

    def action_reject(self):
        self.ensure_one()
        self.registration_id.write({
            'state': 'rejected',
        })
        self.registration_id.message_post(body=_("Rejected: %s") % self.reject_reason)