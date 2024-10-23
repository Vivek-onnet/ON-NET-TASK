from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import math



class SplitInvoiceWizard(models.TransientModel):
    _name = 'split.invoice.wizard'

    invoice_id = fields.Many2one('account.move', string="Invoice")
    line_ids = fields.One2many('split.invoice.line.wizard', 'wizard_id', string="Invoice Lines")
    user_ids = fields.Many2many('res.partner', string="Customers", required=True , domain="[('id', 'in', user_partner_id.ids)]")
    user_partner_id = fields.Many2many('res.partner', string="Customers", required=True ,compute='_compute_user_partner_id')
    split_selection = fields.Selection([('whole_bill', 'Retio wise'), ('product_wise', 'Product wise'), ('amount_wise', 'Amount wise')],string='Split Selection', required=True, default='amount_wise')
    give_percentage = fields.Integer(string='Percentage', required=True, store=True, default=50)
    percentage = fields.Integer(string=' Auto tack Percentage', store=True)
    ratio_display = fields.Char(string="Ratio Display", store=True,help="Displays the ratio in the format 'X:Y'")
    available_product_ids = fields.Many2many('product.product', string="Available Products",compute='_compute_available_product_ids', store=True)
    product_qty = fields.Float(string='Product Quantity', compute='_compute_product_qty', store=True)

    @api.depends('invoice_id','user_ids')
    def _compute_user_partner_id(self):
        """this make sure remove user which already in parent invoice"""
        for record in self:
            if self.invoice_id:
                partner_id = record.invoice_id.partner_id.id
                all_partner_ids = self.env['res.partner'].search([]).ids
                filtered_partner_ids = [pid for pid in all_partner_ids if pid != partner_id]
                record.user_partner_id = [(6, 0, filtered_partner_ids)]  # 6, 0 syntax to set Many2many relations
            else:
                record.user_partner_id = [(5,)]

    @api.constrains('give_percentage')
    def _check_give_percentage(self):
        """this make sure the give percentage is between 0 and 100"""
        for record in self:
            if not (0 < record.give_percentage < 100):
                raise ValidationError(_("The Give Percentage must be between 0 and 100."))


    @api.depends('invoice_id', "line_ids.product_id")
    def _compute_available_product_ids(self):
        """this method computes the products available for splitting based on the selected"""
        for record in self:
            if record.invoice_id:
                product_ids = record.invoice_id.invoice_line_ids.mapped('product_id')
                record.available_product_ids = product_ids


    @api.depends('give_percentage')
    def _compute_product_qty(self):
        """this method calculates the total quantity of products from the original invoice."""
        for record in self:
            invoice = self.env['account.move'].browse(self._context.get('active_id'))
            if invoice:
                all_product_qty = sum(line.quantity for line in invoice.invoice_line_ids)
                record.product_qty = all_product_qty
            else:
                record.product_qty = 0



    @api.onchange('give_percentage','percentage', 'product_qty')
    def _compute_ratio_display(self):
        """this method calculates the display ratio for the split based on user inputs."""
        invoice = self.env['account.move'].browse(self._context.get('active_id'))
        for user in self.user_ids:
            user_lines = self.line_ids.filtered(lambda l: l.user_id == user)
            for line in user_lines:
                if line.quantity < 1 and line.product_id.uom_id.category_id.name == "Unit":
                    raise ValidationError(_("We can not create new invoice for this product  with Quantity = 0."))

        if all(line.product_id.uom_id.category_id.name == "Unit" for line in invoice.invoice_line_ids):
            for record in self:
                for line in invoice.invoice_line_ids:
                    # record.ratio_display = 0
                    # if  line.quantity > 1 and record.product_qty > 2 and record.give_percentage > 0:
                    if  line.quantity > 1 and record.product_qty > 1 and record.give_percentage > 0:
                        ratio = record.give_percentage / 100
                        total_parts = math.ceil(record.product_qty * ratio)
                        record.percentage = round((total_parts / record.product_qty) * 100)
                        second_party_percentage = 100 - int(record.percentage)
                        record.ratio_display = f"{int(record.percentage)}:{int(second_party_percentage)}"

        else:
            for record in self:
                for line in invoice.invoice_line_ids:
                    if record.give_percentage > 0:
                        record.percentage = record.give_percentage
                        second_party_percentage = 100 - record.percentage
                        record.ratio_display = f"{record.percentage}:{second_party_percentage}"

    @api.model
    def default_get(self, fields):
        """Load invoice lines by default based on the parent invoice."""
        result = super(SplitInvoiceWizard, self).default_get(fields)
        invoice = self.env['account.move'].browse(self._context.get('active_id'))
        lines = []
        for line in invoice.invoice_line_ids:
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'total_price': line.price_subtotal,
            }))
        result.update({'line_ids': lines, 'invoice_id': invoice.id})
        return result
    # ###########################################################################

    @api.onchange('line_ids')
    def _onchange_selected(self):
        for line in self.line_ids:
            if line.quantity == 0:
                line.selected = False
            else:
                line.selected = True


    @api.constrains('line_ids')
    def _check_quantities(self):
        """ensure that the total quantitis enter for a product across all lines doesn't exced the available quantity in the original invoice."""
        if self.split_selection in ['product_wise']:
            # line.quantity for line in invoice.invoice_line_ids
            invoice = self.env['account.move'].browse(self._context.get('active_id'))
            product_quantity_map = {}

            for line in self.line_ids:
                if line.product_id in product_quantity_map:
                    product_quantity_map[line.product_id] += line.quantity
                else:
                    product_quantity_map[line.product_id] = line.quantity

            for product, total_quantity in product_quantity_map.items():
                original_invoice_line = invoice.invoice_line_ids.filtered(lambda l: l.product_id == product)

                if original_invoice_line :
                    original_quantity = original_invoice_line[0].quantity  # Get the first matching record


                    for line in self.line_ids:
                        if line.quantity == 0:
                            line.selected = False

                    for line in original_invoice_line:
                        if line.product_id.uom_id.category_id.name == "Unit":
                            if not float(total_quantity).is_integer():
                                raise ValidationError(_(f"The total quantity for product {product.display_name} must be an integer as the unit of measure is 'Unit'."))

                            total_quantity = int(total_quantity)

                            # if total_quantity >= original_quantity and len(self.line_ids) < 2:
                            if total_quantity >= original_quantity and len(invoice.invoice_line_ids) < 2:
                                # print("self.line_ids1", self.line_ids)
                                # print("self.invoice.invoice_line_ids", invoice.invoice_line_ids)

                                raise ValidationError(_(f"The total quantity entered for product {product.display_name} across all lines "
                                    f"({total_quantity}) exceeds the available quantity ({original_quantity}) in the original invoice."))

                        elif line.product_id.uom_id.category_id.name != "Unit":
                            if total_quantity >= original_quantity - 0.01  and len(self.line_ids) < 2:
                                # print("self.line_ids2", self.line_ids)
                                raise ValidationError(_(
                                    f"The total quantity entered for product {product.display_name} across all lines "
                                    f"({total_quantity}) is very low compared to the available quantity ({original_quantity}) in the original invoice."
                                ))

    @api.onchange('user_ids', 'split_selection', 'give_percentage')
    def _onchange_user_and_product(self):
        """in the table,update the product lines based on the selected users and allow manual quantity entry."""

        if self.split_selection == 'product_wise':
            self.line_ids = [(6, 0, [])]
            if self.user_ids:
                invoice = self.env['account.move'].browse(self._context.get('active_id'))
                lines = []
                total_users = len(self.user_ids) + 1  # Including the original invoice user

                for line in invoice.invoice_line_ids:
                    for user in self.user_ids:
                        lines.append((0, 0, {
                            'user_id': user.id,
                            'product_id': line.product_id.id,
                            'quantity': int( line.quantity / total_users),
                            'price_unit': line.price_unit,
                        }))
                self.line_ids = lines

        elif self.split_selection == 'amount_wise':
            self.line_ids = [(6, 0, [])]
            if self.user_ids:
                invoice = self.env['account.move'].browse(self._context.get('active_id'))
                lines = []
                total_users = len(self.user_ids) + 1

                for line in invoice.invoice_line_ids:
                        original_price_per_user = line.price_unit / total_users
                        for user in self.user_ids:
                            lines.append((0, 0, {
                                'user_id': user.id,
                                'product_id': line.product_id.id,
                                'quantity': line.quantity,
                                'price_unit': original_price_per_user,
                                'total_price': line.price_subtotal,
                            }))
                self.line_ids = lines


        elif self.split_selection == 'whole_bill':
            if len(self.user_ids) > 1:
                raise ValidationError(_("You can not split Ratio Wise Bill more than on user"))
            else:
                for line in self.invoice_id.invoice_line_ids:
                    if line.product_id.uom_id.category_id.name == "Unit":
                        if line.quantity == 1:
                            raise ValidationError(_("You can not split Ratio Wise Bill of this type of Product"))
                        if line.quantity == 0:
                            raise ValidationError(_(f"We can not create new invoice for this product with Ratio = 0."))
                    elif line.product_id.uom_id.category_id.name != "Unit":
                        if (line.quantity * self.percentage / 100) < 0.1:
                            raise ValidationError(_(f"We can not create new invoice for this product !!!"))


                self.line_ids = [(6, 0, [])]
                if self.user_ids:
                    invoice = self.env['account.move'].browse(self._context.get('active_id'))
                    lines = []
                    for line in invoice.invoice_line_ids:
                        split_quantity = line.quantity * (self.percentage / 100)
                        if line.product_id.uom_id.category_id.name == "Unit":
                        # if all(line.product_id.uom_id.category_id.name == "Unit" for line in invoice.invoice_line_ids):
                            for user in self.user_ids:
                                lines.append((0, 0, {
                                    'user_id': user.id,
                                    'product_id': line.product_id.id,
                                    'quantity': int(split_quantity),
                                    'price_unit': line.price_unit,
                                }))
                        elif line.product_id.uom_id.category_id.name != "Unit":
                            for user in self.user_ids:
                                lines.append((0, 0, {
                                    'user_id': user.id,
                                    'product_id': line.product_id.id,
                                    'quantity': (line.quantity * self.percentage / 100),
                                    'price_unit': line.price_unit,
                                }))

                    self.line_ids = lines


    def action_split_invoice(self):
        """Split the invoice for each user with progressive product allocation."""
        active_invoice = self.env['account.move'].browse(self._context.get('active_id'))
        if not  self.invoice_id.invoice_line_ids:
            raise ValidationError(
                _(f"You have not any Product in the Cart!!!!"))

        for line in self.invoice_id.invoice_line_ids:
            if not line.quantity or not line :
                raise ValidationError(
                    _(f"We can not create new invoice for this product with Quantity = 0."))

            elif line.quantity and line.quantity == 0.0:
                raise ValidationError(
                    _(f"We can not create new invoice for this product  with Quantity = 0."))

            else:
                if active_invoice.state == 'posted':
                    active_invoice.button_draft()

                for user in self.user_ids:
                    new_invoice_vals = {
                        'partner_id': user.id,
                        'invoice_date': fields.Date.today(),
                        'move_type': active_invoice.move_type,
                        'parent_invoice_id': active_invoice.id,
                        'line_ids': [],
                    }
                    user_lines = self.line_ids.filtered(lambda l: l.user_id == user)

                    for line in user_lines:
                        if line.selected:
                            new_invoice_vals['line_ids'].append((0, 0, {
                                'product_id': line.product_id.id,
                                'quantity': line.quantity,
                                'price_unit': line.price_unit,

                            }))
                            if self.split_selection == 'amount_wise':
                                total_users = len(self.user_ids) + 1
                                original_line = active_invoice.invoice_line_ids.filtered(
                                    lambda l: l.product_id.id == line.product_id.id)
                                if original_line:
                                    original_line.quantity = line.quantity
                                    original_line.price_unit = line.price_unit

                            elif self.split_selection == 'product_wise':

                                original_line = active_invoice.invoice_line_ids.filtered(
                                    lambda l: l.product_id.id == line.product_id.id)
                                if original_line:
                                    all_product_qty = sum(line.quantity for line in active_invoice.invoice_line_ids)
                                    # print("all_product_qty",all_product_qty,(original_line.quantity - line.quantity),original_line.quantity, line.quantity,len(active_invoice.invoice_line_ids))

                                    if all(( o.quantity - line.quantity) < 1 for o in original_line) and len(active_invoice.invoice_line_ids) < 2:
                                        raise ValidationError(
                                            _(f"We can not create new invoice for this product  with Quantity = 0."))
                                    elif all(( o.quantity - line.quantity) < 1 for o in original_line) and original_line.quantity == line.quantity and all_product_qty == original_line.quantity:
                                        raise ValidationError(
                                            _(f"We can not create new invoice for this product  with Quantity = 0."))
                                    else:
                                        original_line.quantity -= line.quantity
                                        original_line.price_unit = original_line.price_unit

                            elif self.split_selection == 'whole_bill':
                                if len(self.user_ids) > 1:
                                    raise ValidationError(_("You can not split Ratio Wise Bill more than on user"))
                                elif line.product_id.uom_id.category_id.name == "Unit" and  line.quantity < 1:
                                    raise ValidationError(_("We can not create new invoice for this product  with Quantity < 1."))
                                else:
                                    original_line = active_invoice.invoice_line_ids.filtered(
                                        lambda l: l.product_id.id == line.product_id.id)
                                    if original_line:
                                        original_line.quantity -= line.quantity
                        if len(self.line_ids) == 1:
                            line = self.line_ids[0]
                            if not line.selected and line.quantity == 0:
                                raise ValidationError(_(
                                    f"We cannot split the invoice for product '{line.product_id.display_name}' with Quantity = 0 and it is not selected."
                                ))


                    # Create a new invoice for the user
                    new_invoice = self.env['account.move'].create(new_invoice_vals)

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'account.move',
                    'view_mode': 'form',
                    'res_id': new_invoice.id,
                    'target': 'current',
                }


class SplitInvoiceLineWizard(models.TransientModel):
    _name = 'split.invoice.line.wizard'

    wizard_id = fields.Many2one('split.invoice.wizard', string="Wizard")
    product_id = fields.Many2one('product.product', string="Product",
                                 domain="[('id', 'in', parent.available_product_ids)]")
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Float(string="Unit Price")
    selected = fields.Boolean(string='Select', default=True)
    user_id = fields.Many2one('res.partner', string="Customer", required=True, domain="[('id', 'in', parent.user_ids)]")

    @api.depends('quantity', 'price_unit')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price_unit

