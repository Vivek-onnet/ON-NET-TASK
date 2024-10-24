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


    @api.depends('membership_states', 'member_lines')
    def _compute_membership(self):
        """Computed Fields for Memberships_id (name//Type) ,this method use to compute "memberships_id"""
        for rec in self:
            if rec.membership_states in [ 'invoiced','expired']:
                memberships = rec.member_lines.filtered(lambda line: line.state in ['invoiced', 'paid', 'free']).mapped('membership_id.id')
                rec.memberships_id = [(6, 0, memberships)]




    @api.depends('membership_states', 'member_lines')
    def _compute_invoiced_date(self):
        """Computed Fields for Invoiced Date"""
        for rec in self:
            for line in rec.member_lines:
                if line.account_invoice_id.payment_state == 'paid' and rec.membership_states == 'invoiced' or rec.membership_states == 'expired' and not line.state == 'canceled'  :
                    line.date = line.account_invoice_id.invoice_date
                    invoiced_lines = rec.member_lines.filtered(lambda line: line.state in [ 'paid'])
                    rec.invoiced_date = invoiced_lines and invoiced_lines[0].date or False


    ### used to automate calculations and derive values based on predefined functions , ensuring data accuracy and reducing manual effort.
    @api.depends('invoiced_date', 'memberships_id')
    def _compute_membership_date(self):
        """ Computed Fields for Exp Date """
        for rec in self:
            if rec.invoiced_date:
                invoiced_date = fields.Date.from_string(rec.invoiced_date)
                durations = rec.memberships_id.mapped('duration_months')
                max_duration = max(durations) * 30 if durations else 0
                rec.exp_date = invoiced_date + timedelta(days=max_duration)
            else:
                rec.exp_date = False



    @api.depends('start_date', 'invoiced_date', 'member_lines.state', 'membership_states', 'memberships_id')
    def _compute_action_done(self):
        """Computed Fields for ACTION STATUS BAR"""
        today = fields.Date.today()
        for rec in self:
            expired_memberships, new_memberships = self._find_membership_updates(rec, today)
            has_invoiced_or_paid, has_reversed = self._check_payment_status(rec)

            # Remove expired or reversed memberships
            if expired_memberships:
                rec.memberships_id = [(3, membership.id) for membership in expired_memberships]

            # Add new memberships
            if new_memberships:
                rec.memberships_id = [(4, membership.id) for membership in new_memberships]

            # Set membership state
            rec._set_membership_state(has_invoiced_or_paid, has_reversed)


    def _find_membership_updates(self, rec, today):
        expired_memberships = []
        new_memberships = []
        for line in rec.member_lines:
            membership = line.membership_id.product_tmpl_id
            invoice = line.account_invoice_id
            exp_date = False

            if line.state and line.state not in ['old', 'none']:
                if invoice and invoice.payment_state in ['invoiced', 'paid']:
                    exp_date = self._compute_membership_expiry(invoice, membership)
                if exp_date and exp_date <= today:
                    line.state = 'none'
                    expired_memberships.append(membership)
                elif exp_date and membership not in rec.memberships_id:
                    new_memberships.append(membership)
        return expired_memberships, new_memberships

    def _check_payment_status(self, rec):
        has_invoiced_or_paid = False
        has_reversed = False
        for line in rec.member_lines:
            invoice = line.account_invoice_id
            if line.state and line.state not in ['old', 'none']:
                if invoice and invoice.payment_state in ['invoiced', 'paid']:
                    has_invoiced_or_paid = True
                elif invoice and invoice.payment_state == 'reversed':
                    has_reversed = True
        return has_invoiced_or_paid, has_reversed

    def _set_membership_state(self, has_invoiced_or_paid, has_reversed):
        if has_invoiced_or_paid:
            for rec in self.member_lines:
                if any(line.state in ['paid', 'invoiced'] for line in self.member_lines) and self.memberships_id:
                    if (line.state not in ['old', 'canceled'] for line in self.member_lines) and self.memberships_id:
                        self.membership_states = 'invoiced'
            # self.membership_states = 'invoiced'
        elif not self.memberships_id:
            self.invoiced_date = False
            self.exp_date = False
            self.membership_states = 'in_consultation'
            # if self.start_date and not self.invoiced_date:
            #     self.membership_states = 'in_consultation'
            self.membership_states = 'in_consultation'
        if not self.start_date and not self.invoiced_date and not self.exp_date:
            self.membership_states = 'pending'
        elif any(line.state == 'none' for line in self.member_lines):
            for line in self.member_lines:
                invoice = line.account_invoice_id
                if invoice and invoice.payment_state != 'reversed' and line.state in ['none']:
                    self.membership_states = 'expired'

    def _compute_membership_expiry(self, invoice, membership):
        if invoice and invoice.invoice_date and membership.duration_months:
            return invoice.invoice_date + relativedelta(months=membership.duration_months)
        return False


    #  action button statusbar :

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
        for rec in self:
            self._cancel_invoices(rec)
            self._remove_expired_memberships(rec)
            rec.action_is_consultation()

    def _cancel_invoices(self, rec):
        excluded_invoices = self.env['account.move'].search([('partner_id', '=', rec.id), ('payment_state', '=', 'reversed'), ('state', '=', 'posted')])
        invoices = self.env['account.move'].search([('partner_id', '=', rec.id), ('id', 'not in', excluded_invoices.ids)])
        if not excluded_invoices:
            moves_to_reset_draft = invoices.filtered(lambda inv: inv.state != 'draft')
            if moves_to_reset_draft:
                moves_to_reset_draft.button_draft()
            invoices.button_cancel()


    def _remove_expired_memberships(self, rec):
        expired_memberships = []
        excluded_invoices = self.env['account.move'].search([('partner_id', '=', rec.id), ('payment_state', '=', 'reversed'), ('state', '=', 'posted')])
        for line in rec.member_lines:
            membership = line.membership_id.product_tmpl_id
            invoice = line.account_invoice_id
            if excluded_invoices and line.state and line.state in ['none']:
                if invoice and invoice.payment_state == 'reversed' and membership in rec.memberships_id:
                    expired_memberships.append(membership)
                    if expired_memberships:
                        rec.memberships_id = [(3, membership.id) for membership in expired_memberships]
            elif not excluded_invoices:
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

    # We can use this method to call a function defined within any model WITH passing any parameters.
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


    # constraint will raise a validation error if the start date is set to a date before the current date.
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        """Constraint for the Start Date"""
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


    def action_membership_invoice_view(self):
        """Get Action For Buy Membership View """
        view = self.env['ir.actions.act_window']._for_xml_id('membership.action_membership_invoice_view')
        # print("view......",view)
        return view


    def action_membership_invoice_wizard(self):
        """Get ActionFor Manage Membership Wizard"""
        view = self.env['ir.actions.act_window']._for_xml_id('gym_management.action_membership_invoice_wizard')
        # print("view......",view)
        return view

