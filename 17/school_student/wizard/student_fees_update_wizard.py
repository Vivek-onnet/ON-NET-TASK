from odoo import models, fields, api


# - ** Wizards **: Wizards in Odoo are used for creating interactive dialogs with the user. These are typically transient models used for short-term data operations.

# - **Transient Models**: Unlike regular models, transient models are not persistent and are automatically deleted from the database after 5 miniut of time.

class StudentFeesUpdateWizard(models.TransientModel):
    _name = 'student.fees.update.wizard'

    total_fees = fields.Float(string="Fees")


    #  Implement the method to perform the desired action when the button in the wizard is clicked.
    def update_student_fees(self):
        rec = self.env['school.student'].browse(self._context.get('active_ids')).update({'total_fees':self.total_fees})
        print("Successfully Updated",rec)
        return True


### Summary of wizard :---->
# - **Create Wizard Model**: Define a transient model with necessary fields.
# - **Trigger Wizard**: Create a method in the related model to open the wizard.
# - **Define Views**: Create the form view for the wizard and actions to open it.
# - **Add Button**: Add a button in the related model's form view to trigger the wizard.
# - **Implement Action**: Define the method in the wizard model to perform the desired action.
