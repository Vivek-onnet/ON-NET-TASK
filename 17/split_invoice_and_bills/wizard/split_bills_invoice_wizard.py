from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import math


class SplitInvoiceWizard(models.TransientModel):
    _name = 'split.invoice.wizard'

    invoice_id = fields.Many2one('account.move', string="Invoice")
    line_ids = fields.One2many('split.invoice.line', 'wizard_id', string="Invoice Lines")
    customer_ids = fields.Many2many('res.partner', string="Customers")
    customers_id = fields.Many2one('res.partner', string="Customers")
    split_selection = fields.Selection([('whole_bill', 'Ratio wise'), ('product_wise', 'Product wise'), ('amount_wise', 'Amount wise')],string='Split Selection', required=True, default='amount_wise')
    give_percentage = fields.Integer(string='Percentage', required=True, store=True, default=50)
    percentage = fields.Integer(string=' Auto tack Percentage', store=True)
    ratio_display = fields.Char(string="Ratio Display", store=True, help="Displays the ratio in the format 'X:Y'")
    available_product_ids = fields.Many2many('product.product', string="Available Products",compute='_compute_available_product_ids', store=True)
    product_qty = fields.Float(string='Product Quantity', compute='_compute_product_qty', store=True)



    @api.model
    def default_get(self, fields):
        """Load invoice lines by default based on the parent invoice.(geting the invoice id)"""
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


    @api.constrains('give_percentage')
    def _check_give_percentage(self):
        """this make sure the give percentage is between 0 and 100"""
        for record in self:
            if not (0 < record.give_percentage < 100):
                raise ValidationError(_("The Give Percentage must be between 0 and 100."))
    @api.onchange('customers_id', 'split_selection')
    def _onchange_customer_ids_id(self):
        if self.split_selection == 'whole_bill':
            self.customer_ids = self.customers_id

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
            record.product_qty = 0
            if self.invoice_id:
                all_product_qty = sum(line.quantity for line in self.invoice_id.invoice_line_ids)
                record.product_qty = all_product_qty


    @api.onchange('give_percentage','customers_id','customers_id','product_qty')
    def _onchange_ratio_display(self):
        """Compute the ratio for splitting the invoice based on the given percentage and product quantity."""
        for record in self:
            print("record",record,self)
            if record.give_percentage <= 0:
                continue
            if all(line.product_id.uom_id.category_id.name == "Unit" for line in self.invoice_id.invoice_line_ids):
                self._count_ratio_unit(record)
            else:
                record.percentage = record.give_percentage
                second_party_percentage = 100 - record.percentage
                record.ratio_display = f"{record.percentage}:{second_party_percentage}"

    def _count_ratio_unit(self,record):
        for line in self.invoice_id.invoice_line_ids:
            if line.quantity > 1 and record.product_qty > 1 and record.give_percentage > 0:
                ratio = record.give_percentage / 100
                total_parts = math.ceil(record.product_qty * ratio)
                record.percentage = round((total_parts / record.product_qty) * 100)
                second_party_percentage = 100 - record.percentage
                record.ratio_display = f"{record.percentage}:{second_party_percentage}"

    @api.onchange('line_ids')
    def _onchange_update_selected(self):
        """
        Updates the 'selected' field of line items based on the 'quantity'.
        If the quantiti is zero, 'selected' is set to False; otherwise, it is set to True.
        """
        for line in self.line_ids:
            line.selected = line.quantity > 0

    @api.constrains('line_ids')
    def _check_quantities(self):
        """Ensure that the total quantities entered for a product across all lines ,don't exceed the available quantity in the original invoice."""
        if self.split_selection != 'product_wise':
            return
        product_quantity_map = {}
        for line in self.line_ids:
            product_quantity_map[line.product_id] = product_quantity_map.get(line.product_id, 0) + line.quantity
            self._quantity_constrains(product_quantity_map)

    def _quantity_constrains(self,product_quantity_map):
        for product, total_quantity in product_quantity_map.items():
            original_line = self.invoice_id.invoice_line_ids.filtered(lambda l: l.product_id == product)
            if original_line:
                original_quantity = original_line[0].quantity
                if all(line.quantity == 0 for line in self.line_ids):
                    raise ValidationError(_("Quantity cannot be zero."))
                for line in self.line_ids:
                    if line.quantity == 0:
                        line.selected = False
                if product.uom_id.category_id.name == "Unit" and not float(total_quantity).is_integer():
                    raise ValidationError(
                        _(f"The total quantity for product {product.display_name} must be an integer as the unit of measure is 'Unit'."))
                if total_quantity >= original_quantity:
                    raise ValidationError(
                        _(f"The total quantity entered for product {product.display_name} ({total_quantity}) exceeds the available quantity ({original_quantity}) in the original invoice."))
                if product.uom_id.category_id.name != "Unit" and  total_quantity >= original_quantity  and  len(self.line_ids) < 2 :
                        raise ValidationError(
                            _(f"wEntered quantity for product {product.display_name} ({total_quantity}) is too low compared to the available quantity ({original_quantity}). The minimum quantity should be 0.2 in both invoices."))

    @api.onchange('customer_ids', 'split_selection', 'give_percentage')
    def _onchange_user_and_product(self):
        """Update product lines based on selected users and split selection."""
        self.line_ids = [(6, 0, [])]
        if not self.customer_ids:
            return
        total_users = len(self.customer_ids) + 1
        lines = []
        for line in self.invoice_id.invoice_line_ids:
            if self.split_selection == 'product_wise':
                self._update_product_line_for_product_wise(total_users,lines,line)

            elif self.split_selection == 'amount_wise':
                self._update_product_line_for_amount_wise(total_users,lines,line)

            elif self.split_selection == 'whole_bill':
                self._update_product_line_for_whole_bill(lines,line)
        self.line_ids = lines

    def _update_product_line_for_product_wise(self,total_users,lines,line):
        # for line in self.invoice_id.invoice_line_ids:
        quantity_per_user = int(line.quantity / total_users)
        for user in self.customer_ids:
            lines.append(self._prepare_invoice_line(user, line, quantity_per_user, line.price_unit))

    def _update_product_line_for_amount_wise(self, total_users, lines,line):
        # for line in self.invoice_id.invoice_line_ids:
        price_per_user = line.price_unit / total_users
        for user in self.customer_ids:
            print("user",user)
            lines.append(self._prepare_invoice_line(user, line, line.quantity, price_per_user))
    def _update_product_line_for_whole_bill(self, lines,line):
        # for line in self.invoice_id.invoice_line_ids:
        self._validate_whole_bill(line)
        split_quantity = line.quantity * (self.percentage / 100)
        int_split_quantity = int(split_quantity)
        for user in self.customer_ids:
            if line.product_id.uom_id.category_id.name == "Unit":
                lines.append(self._prepare_invoice_line(user, line, int_split_quantity, line.price_unit))
            else:
                lines.append(self._prepare_invoice_line(user, line, split_quantity, line.price_unit))


    def _prepare_invoice_line(self, user, line, quantity, price_unit):
        """Helper function to prepare invoice line dictionary."""
        return (0, 0, {
            'user_id': user.id,
            'product_id': line.product_id.id,
            'quantity': quantity,
            'price_unit': price_unit,
        })

    def _validate_whole_bill(self, line):
        """Validation logic for 'whole_bill' selection."""
        uom_category = line.product_id.uom_id.category_id.name
        split_quantity = line.quantity * (self.percentage / 100)
        if uom_category == "Unit" and (line.quantity == 1 or line.quantity == 0) or split_quantity == line.quantity:
            raise ValidationError(_("Cannot split this product with quantity of 1 or 0."))
        if uom_category != "Unit" and split_quantity < 0.5:
            raise ValidationError(_("Cannot split this product with quantity less then 0.5"))


    def action_split_invoice(self):
        """Split the invoice for each user based on selected method."""
        # Check if invoice has lines
        self._action_split_invoice_constrains()

        if self.invoice_id.state == 'posted':
            self.invoice_id.button_draft()

        for user in self.customer_ids:
            new_invoice_vals = self._new_invoice_vals(user)

            user_lines = self.line_ids.filtered(lambda l: l.user_id == user and l.selected)
            if not user_lines:
                raise ValidationError(_(f"No products selected for user {user.name}."))

            for line in user_lines:
                original_line = self.invoice_id.invoice_line_ids.filtered(
                    lambda l: l.product_id.id == line.product_id.id)

                if not original_line:
                    raise ValidationError(_("Product does not exist in the original invoice."))

                # Split invoice by amount
                if self.split_selection == 'amount_wise':
                    original_line.quantity = line.quantity
                    original_line.price_unit = line.price_unit

                # Split invoice by product quantity
                elif self.split_selection == 'product_wise':
                    total_qty = sum(l.quantity for l in self.invoice_id.invoice_line_ids)
                    if original_line.product_id.uom_id.category_id.name == "Unit" and total_qty <= line.quantity:
                        raise ValidationError(_("Cannot split invoice for this product with quantity < 1."))
                    original_line.quantity -= line.quantity

                # Split entire bill
                elif self.split_selection == 'whole_bill':
                    if original_line.product_id.uom_id.category_id.name == "Unit" and line.quantity < 1:
                        raise ValidationError(_("Cannot create invoice with quantity < 1."))
                    original_line.quantity -= line.quantity

                new_invoice_vals['line_ids'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                }))

            # Create a new invoice for the user
            new_invoice = self.env['account.move'].create(new_invoice_vals)

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': new_invoice.id,
                'target': 'current',
            }

    def _action_split_invoice_constrains(self):
        """Check if invoice has lines"""
        if not self.customer_ids and not self.customers_id:
            raise ValidationError(
                _(f"Please select at least one user."))
        if not self.invoice_id.invoice_line_ids:
            raise ValidationError(_("No products in the invoice."))

    def _new_invoice_vals(self,user):
        return {
                'partner_id': user.id,
                'invoice_date': fields.Date.today(),
                'move_type': self.invoice_id.move_type,
                'parent_invoice_id': self.invoice_id.id,
                'line_ids': [],
            }



class SplitInvoiceLine(models.TransientModel):
    _name = 'split.invoice.line'

    wizard_id = fields.Many2one('split.invoice.wizard', string="Wizard")
    product_id = fields.Many2one('product.product', string="Product",
                                 domain="[('id', 'in', parent.available_product_ids)]")
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Float(string="Unit Price")
    selected = fields.Boolean(string='Select', default=True)
    user_id = fields.Many2one('res.partner', string="Customer", required=True, domain="[('id', 'in', parent.customer_ids)]")

    @api.depends('quantity', 'price_unit')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.price_unit
#
