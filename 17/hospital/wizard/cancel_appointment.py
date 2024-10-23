from odoo import api, fields, models, _

class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment", required=True)
    reason = fields.Text(string="Reason", required=True)

    def action_cancel_appointment(self):
        # Ensure that only one record is bing processed
        self.ensure_one()

        # Retrieve the appointment record
        appointment = self.appointment_id

        # If the appointment exists, update its state to 'cancel' and set the cancel reason
        if appointment:
            appointment.write({
                'state': 'cancel',  # Set the state to 'cancel'
                })

            # Return an action to reload the client view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

