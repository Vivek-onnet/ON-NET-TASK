from odoo import api, exceptions, fields, models
from datetime import timedelta, date
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re


class GymMember(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(string='Name', required=True, store=True)
    parent_id = fields.Many2one('res.partner', domain="[('company_type','!=','person')]")
    memberships_id = fields.Many2many('product.template', 'membership_rel', 'partner_id', 'memberships_ids',domain="[('membership', '=', True)]", string='Memberships', store=True,compute="_compute_membership")
    member_lines = fields.One2many('membership.membership_line', 'partner', string='Membership')

    gym = fields.Boolean(string='Active User')
    gymid = fields.Char(string='ID', readonly=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],required=True)
    bdate = fields.Date(string="Birth Date", required=True)
    age = fields.Integer(compute='_compute_age', string="Age", store=True)
    weight = fields.Float(string='Weight (kg)', required=True)
    height = fields.Float(string='Height (cm)', required=True, digits=(4, 2))
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    health_status = fields.Char(string='Health Status', compute='_compute_health_status', store=True)
    start_date = fields.Date(string='Start Date', date_format='%d-%m-%Y', store=True)
    invoiced_date = fields.Date(string='Invoiced Date', date_format='%d-%m-%Y', store=True,compute='_compute_invoiced_date')
    membership_id = fields.Many2one('product.template', domain="[('membership', '=', True)]", string='Membership',store=True)
    exp_date = fields.Date(string='Expiration Date', date_format='%d-%m-%Y', compute='_compute_membership_date',store=True)
    company_type = fields.Selection([('person', 'Member'),('company', 'Trainer')], default='person', store=True)
    member_workout_ids = fields.One2many('gym_management.member_workout', 'members_id', string='Workout Plans')
    attendance_ids = fields.One2many('hr.attendance', 'name', string='Attendance Records')

    member_diet_ids = fields.One2many('gym_management.member_diet', 'member_id', string='Diet Plans')
    membership_states = fields.Selection([('pending', 'Non Member'), ('in_consultation', 'In Consultation'), ('invoiced', 'Paid'),('expired', 'Expired')], compute='_compute_action_done', store=True)



    """################  Computed Fields for Memberships_id (name//Type)  ################"""

    # this mehtod use to compute "memberships_id"
    @api.depends('membership_states', 'member_lines')
    def _compute_membership(self):
        for rec in self:
            if rec.membership_states in [ 'invoiced','expired']:
                memberships = rec.member_lines.filtered(lambda line: line.state in ['invoiced', 'paid', 'free']).mapped('membership_id.id')
                rec.memberships_id = [(6, 0, memberships)]

    """################  Computed Fields for Invoiced Date  ################"""



    @api.depends('membership_states', 'member_lines')
    def _compute_invoiced_date(self):
        for rec in self:
            for line in rec.member_lines:
                if line.account_invoice_id.payment_state == 'paid' and rec.membership_states == 'invoiced' or rec.membership_states == 'expired' and not line.state == 'canceled'  :
                    line.date = line.account_invoice_id.invoice_date
                    invoiced_lines = rec.member_lines.filtered(lambda line: line.state in [ 'paid'])
                    rec.invoiced_date = invoiced_lines and invoiced_lines[0].date or False

    """################  Computed Fields for Exp Date  : ################"""
    ### used to automate calculations and derive values based on predefined functions , ensuring data accuracy and reducing manual effort.


    @api.depends('invoiced_date', 'memberships_id')
    def _compute_membership_date(self):
        for rec in self:
            if rec.invoiced_date:
                invoiced_date = fields.Date.from_string(rec.invoiced_date)
                durations = rec.memberships_id.mapped('duration_months')
                max_duration = max(durations) * 30 if durations else 0
                rec.exp_date = invoiced_date + timedelta(days=max_duration)
            else:
                rec.exp_date = False

    """################  Computed Fields for ACTION STATUS BAR  : ################"""


    @api.depends('start_date', 'invoiced_date', 'member_lines.state','membership_states','memberships_id')
    def _compute_action_done(self):
        today = fields.Date.today()
        for rec in self:
            expired_memberships = []  # List to store expired memberships to remove
            new_memberships = []  # List to store new memberships to add
            has_invoiced_or_paid = False
            has_reversed = False
            for line in rec.member_lines:
                membership = line.membership_id.product_tmpl_id  # Access product.template via product.product
                invoice = line.account_invoice_id
                exp_date = False

                #process only valid states (excluding 'old' and 'none')
                if line.state and line.state not in ['old', 'none']:
                    #check for valid invoices (exclude 'reversed'), because we not need it
                    if invoice and invoice.payment_state in ['invoiced', 'paid']:
                        has_invoiced_or_paid = True  # Track that there's an 'invoiced' or 'paid' line
                        duration = membership.duration_months
                        invoiced_date = invoice.invoice_date
                        if invoiced_date and duration:
                            #calculate expiration date
                            exp_date = invoiced_date + relativedelta(months=duration)

                    #if the payment state has been reversed, remove the membership
                    elif invoice and invoice.payment_state == 'reversed':
                        has_reversed = True
                        #remove membership from rec.memberships_id if the payment is reversed
                        if membership in rec.memberships_id:
                            expired_memberships.append(membership)

                #if expiration date ==yes , check if it's expired
                if exp_date:
                    if exp_date <= today:
                        line.state = 'none'
                        # if membership is expired, mark it for removal
                        if membership in rec.memberships_id:
                            expired_memberships.append(membership)
                    else:
                        #mark membership for adding if it is not expired
                        if membership not in rec.memberships_id:
                            new_memberships.append(membership)



            #now we remove expired or reversed memberships from the Many2many field
            if expired_memberships:
                rec.memberships_id = [(3, membership.id) for membership in expired_memberships]

            #add new memberships to the Many2many field
            if new_memberships:
                rec.memberships_id = [(4, membership.id) for membership in new_memberships]

            # set membership state based on payment states:
            # priority 1: if there's any invoiced or paid, set to 'invoiced'
            if has_invoiced_or_paid:
                # state = rec.memberships_id == [(6, 0, [])]
                for line in rec.member_lines:
                    if any(line.state in ['paid','invoiced'] for line in rec.member_lines) and rec.memberships_id :
                        if (line.state not in ['old','canceled'] for line in rec.member_lines) and  rec.memberships_id:
                            rec.membership_states = 'invoiced'


            # if all are reversed and no invoiced or paid, set to 'in_consultation'
            if not rec.memberships_id:
                rec.invoiced_date = False
                rec.exp_date = False
                # if rec.start_date and not rec.invoiced_date and has_reversed and not has_invoiced_or_paid and a and rec.memberships_id == [(6, 0, [])] :
                if rec.start_date and not rec.invoiced_date :
                    rec.membership_states = 'in_consultation'
                rec.membership_states = 'in_consultation'

            # set to 'panding' if no start date and no invoice date
            if rec.start_date == False and rec.invoiced_date == False and rec.exp_date == False:
                rec.membership_states = 'pending'

            # set to 'expired' if any line has state 'none' and valid invoices are not reversed
            elif any(line.state == 'none' for line in rec.member_lines):
                for line in rec.member_lines:
                    invoice = line.account_invoice_id
                    if invoice and invoice.payment_state != 'reversed' and line.state in ['none']:
                        rec.membership_states = 'expired'



    """################  action button stutusbar : ################"""

    def action_is_consultation(self):
        """ set membership state to 'in_consultation' """
        for rec in self:
            # rec.membership_states = 'in_consultation'
            if rec.start_date != False and rec.invoiced_date == False and rec.exp_date == False and not rec.memberships_id:
                rec.membership_states = 'in_consultation'


    def action_done(self):
            """ Set membership state to 'invoiced' """
            for rec in self:
                rec.membership_states = 'invoiced'



    def action_cancel(self):
        """ Set membership state to 'canceled' """
        for rec in self:
            expired_memberships = []
            for line in rec.member_lines:
                # Search for invoices that are reversed and posted
                excluded_invoices = self.env['account.move'].search([
                    ('partner_id', '=', rec.id),
                    ('payment_state', '=', 'reversed'),
                    ('state', '=', 'posted')
                ])

                membership = line.membership_id.product_tmpl_id  # Access product.template via product.product
                invoice = line.account_invoice_id
                if excluded_invoices and line.state and line.state in ['none']:
                    # Dynamically calculate exp_date based on the membership's duration and invoiced_date
                     if invoice and invoice.payment_state in ['reversed']:
                         if membership in rec.memberships_id:
                             expired_memberships.append(membership)
                             if expired_memberships:
                                 rec.memberships_id = [(3, membership.id) for membership in expired_memberships]


                # Now search for all invoices related to this partner, but exclude the above invoices
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', rec.id),
                    ('id', 'not in', excluded_invoices.ids)  # Exclude the invoices you don't want to cancel
                ])
                if not excluded_invoices:
                    # Process invoices that are not excluded
                    moves_to_reset_draft = invoices.filtered(lambda inv: inv.state != 'draft')
                    if moves_to_reset_draft:
                        # Set to draft if not already in draft state
                        moves_to_reset_draft.button_draft()
                    # Cancel the invoices that are not excluded
                    invoices.button_cancel()
                # For lines with no excluded invoices, set the state to 'canceled'
                if not excluded_invoices:
                    line.state = 'canceled'
                    if line.state == 'canceled':
                        rec.invoiced_date = False
                        rec.exp_date = False
                        rec.action_is_consultation()
                        rec.memberships_id = [(6, 0, [])]

    def action_draft(self):
        """ Reset membership state to 'pending' """
        for rec in self:
            # rec.membership_states = 'pending'
            if rec.start_date == False and rec.invoiced_date == False and rec.exp_date == False:
                rec.membership_states = 'pending'




    """################  action button Membership Renew : ################"""

    def action_state(self):
        """Renew the membership for a gym member by extending the expiration date."""
        for rec in self:
            for line in rec.member_lines:
                membership = line.membership_id
                invoice = line.account_invoice_id
                # Check for reversed payment state
                if invoice and invoice.payment_state != 'reversed':

                    # rec.is_renewing = True  # Set the renewing flag
                    if any(line.state == 'none' for line in rec.member_lines):
                        if invoice.payment_state != 'reversed':
                            rec.invoiced_date = False
                            rec.exp_date = False
                            rec.memberships_id = [(6, 0, [])]

                            old_membership_lines = rec.member_lines.filtered(lambda l: l.state == 'none' and l.account_invoice_id and l.account_invoice_id.payment_state != 'reversed')

                            if old_membership_lines:
                                first_old_membership = old_membership_lines[0].membership_id

                                # Update the state of the first old membership line to 'none'
                                first_old_membership_line = old_membership_lines[0]
                                first_old_membership_line.write({'state': 'old'})  # Save the change

                                # Search for an existing invoice where product_id matches the first old membership
                                invoice = self.env['membership.invoice'].search(
                                    [('product_id', '=', first_old_membership.id)], limit=1)
                                # Return the updated view to the frontend
                                view = self.env['ir.actions.act_window']._for_xml_id(
                                    'membership.action_membership_invoice_view')
                                view.update({
                                    'context': dict(self.env.context, default_product_id=first_old_membership.id,
                                                    active_id=invoice.id,
                                                    active_model='membership.invoice'),
                                })
                                return view
                    return True

    """##############################################################################"""
    """################  Function call from XML WITH parameters : ################"""

    # We can use this method to call a function defined within any model WITH passing any parameters.

    @api.model
    def _change_id_with_para(self, add_string):
        """this method is used to add roll number//ID to the Gym profile"""
        records = self.search([('is_company', '=', False)])
        for record in records:
            record.gymid = add_string + "GMID" + str(record.id)

        records = self.search([('is_company', '=', True)])
        for record in records:
            record.gymid = add_string + "TID" + str(record.id)

    """################  Constraint for the Birth Date  ################"""
    # constraint will raise  validation error if the selected birth date is in the future

    @api.constrains('bdate')
    def _check_bdate(self):
        for record in self:
            if record.bdate and record.bdate >= date.today():
                raise ValidationError(_("Birth Date must be in the past."))

    """################  Constraint for the Email  ################"""
    # constraint will raise  validation error if the email is not valid

    @api.constrains('email')
    def _check_email(self):
        email_regex = r'^[a-z0-9\.-]+@[a-z0-9\.-]+\.[a-z]{2,}$'

        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(_("Please enter a valid email address."))

    """################  Constraint for the Phone number  ################"""
    # constraint will raise  validation error if the Phone number is not valid

    @api.constrains('phone')
    def _check_phone(self):
        phone_regex = r'^[0-9]{10}$'

        for record in self:
            if record.phone and not re.match(phone_regex, record.phone):
                raise ValidationError(_("Please enter a valid Phone number."))

    """################ Computed Fields for Age// Date : ################"""

    ## used to automate calculations and derive values based on predefined functions , ensuring data accuracy and reducing manual effort.
    ## age = fields.Integer(compute='_compute_age', string="Age", store=True) #  store = True attributes is used to STORE the field record in the DATABASE
    @api.depends('bdate')
    def _compute_age(self):
        for rec in self:
            if rec.bdate:
                rec.age = (fields.Date.today() - rec.bdate).days // 365
            else:
                rec.age = 0

    """################  Computed Fields for Health Status and BMI  ################"""

    @api.depends('bmi')
    def _compute_health_status(self):
        for record in self:
            if record.bmi < 18.5:
                record.health_status = 'Underweight'
            elif 18.5 <= record.bmi < 24.9:
                record.health_status = 'Healthy'
            elif 25 <= record.bmi < 29.9:
                record.health_status = 'Overweight'
            else:
                record.health_status = 'Obese'

    """################  Constraint for the Start Date  ################"""
    # constraint will raise a validation error if the start date is set to a date before the current date.

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.height > 0:  # Check if height is valid
                height_in_meters = record.height / 100.0
                record.bmi = record.weight / (height_in_meters ** 2)
            else:
                record.bmi = 0.0  # Set BMI to 0 if height is invalid

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date and record.start_date < date.today():
                raise ValidationError("Start Date cannot be in the past.")

    """################  Computed Fields for Display name  ################"""

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name

    @api.onchange('bdate')
    def _compute_gym(self):
        for record in self:
            if record.bdate:
                record.gym = True
            else:
                record.gym = False

    """################ Get Action For Buy Membership View  ################"""

    def action_membership_invoice_view(self):
        view = self.env['ir.actions.act_window']._for_xml_id('membership.action_membership_invoice_view')
        # print("view......",view)
        return view

    """################ Get ActionFor Manage Membership Wizard  ################"""

    def action_membership_invoice_wizard(self):
        view = self.env['ir.actions.act_window']._for_xml_id('gym_management.action_membership_invoice_wizard')
        # print("view......",view)
        return view

