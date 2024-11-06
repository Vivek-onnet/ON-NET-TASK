from odoo import models, fields, api, exceptions, _

class Attendance(models.Model):
    _inherit = 'hr.attendance'

    gym = fields.Boolean(string='Gym', default=True ,invisible=True)
    name = fields.Many2one('res.partner', string='Name',domain="[('gym', '=', True)]", required=True)


    @api.constrains('check_in', 'check_out')
    def _check_validity(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_in >= attendance.check_out:
                    raise exceptions.ValidationError(_('Check-out time must be after check-in time.'))



    def _assign_employee(self, vals):
        # Automatically assign employee_id if not provided
        if 'employee_id' not in vals or not vals.get('employee_id'):
            employee = self.env['hr.employee'].browse(1)  # Automatically assign employee with ID 1
            if employee:
                vals['employee_id'] = employee.id
        return vals

    @api.model
    def create(self, vals):
        vals = self._assign_employee(vals)
        return super(Attendance, self).create(vals)

    def write(self, vals):
        vals = self._assign_employee(vals)
        return super(Attendance, self).write(vals)


