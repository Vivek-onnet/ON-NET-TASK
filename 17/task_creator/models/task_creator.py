from odoo import models, fields, _, api
from odoo.exceptions import  ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    task_count = fields.Integer(
        string="Number of Tasks",
        default=1,
        help="Number of tasks to create when this product is selected in a sale order."
    )

    @api.constrains('task_count')
    def _check_task_count(self):
        self.ensure_one()
        if self.service_tracking in ['task_in_project', 'task_global_project'] and  self.task_count < 1:
            raise ValidationError(_("Number of tasks should be greater than 0"))


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task(self, project):
        res = super(SaleOrderLineInherit,self)._timesheet_create_task(project)
        self.ensure_one()

        task_count = self.product_id.task_count or 1
        tasks = []
        for count in range(2, task_count + 1):
            values = self._timesheet_create_task_prepare_values(project)
            values['name'] += f" ({count})"
            task = self.env['project.task'].sudo().create(values)
            tasks.append(task)
            task_msg = _(
                "This task has been created from: %s (%s)",
                self.order_id._get_html_link(),
                self.product_id.name
            )
            task.message_post(body=task_msg)

        return res
