from odoo import http,fields,_
from datetime import datetime
from odoo.http import route, request, content_disposition
from werkzeug.exceptions import NotFound
from werkzeug.urls import url_encode




class CricketBoxPortal(http.Controller):

    @http.route('/my/cricket_box', type='http', auth="public", website=True)
    def cricket_boxes(self, **kwargs):
        cricket_boxes = request.env['cricket.box'].sudo().search([])
        return request.render('cricket_box_booking_management.portal_cricket_boxes', {
            'cricket_boxes': cricket_boxes
        })

    @http.route('/my/cricket_box/<int:box_id>', type='http', auth="user", website=True)
    def cricket_box_details(self, box_id, **kwargs):
        cricket_box = request.env['cricket.box'].sudo().browse(box_id)
        # print(cricket_box.state)
        return request.render('cricket_box_booking_management.portal_cricket_box_details', {
            'cricket_box': cricket_box,
            'select_dates': cricket_box.select_dates,
        })



    @http.route('/my/cricket_box/registrations', website=True, auth='user')
    def cricket_box_registration_menu_list(self, **kwargs):
        registration_name = kwargs.get('name')
        current_user = request.env.user

        is_admin = current_user.has_group('base.group_system')


        if not registration_name:
            if not is_admin:
                registrations = request.env['cricket.box.registration'].sudo().search([('partner_id.name', '=', current_user.name)])
                return request.render("cricket_box_booking_management.cricket_box_template_data",{'registrations': registrations})
            registrations_admin = request.env['cricket.box.registration'].sudo().search([])
            return request.render("cricket_box_booking_management.cricket_box_template_data",{'registrations': registrations_admin})

        registration_sudo = request.env['cricket.box.registration'].sudo().search([('name', '=', registration_name)], limit=1)
        return request.render("cricket_box_booking_management.cricket_box_template_data",
                              {'registrations': registration_sudo})

    @route(['/my/cricket_box/download_pass/<string:name>'], type='http', auth='user', methods=['GET'])
    def download_cricket_box_pass(self, **kwargs):
        """
        Generates and downloads a PDF pass for a cricket box registration.
        :param kwargs: Dictionary containing filter criteria like `name`.
        """
        registration_name = kwargs.get('name')
        if not registration_name:
            raise NotFound()

        registration_sudo = request.env['cricket.box.registration'].sudo().search([('name', '=', registration_name)], limit=1)
        if not registration_sudo:
            raise NotFound()

        report_template = 'cricket_box_booking_management.action_report_cricket_box_pass'

        pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(report_template, [registration_sudo.id])[0]

        pdf_name = f"Cricket_Box_Pass_{registration_sudo.name}.pdf"

        pdf_http_headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', content_disposition(pdf_name)),
        ]

        return request.make_response(pdf_content, headers=pdf_http_headers)

    @route(['/my/cricket_box/cancel/<string:name>'], type='http', auth='user', methods=['GET'])
    def cancel_cricket_box_booking(self, **kwargs):
        """ Function for cancelling a cricket box booking. """
        # get registration name
        registration_name = kwargs.get('name')
        if not registration_name:
            raise NotFound()

        registration_sudo = request.env['cricket.box.registration'].sudo().search([('name', '=', registration_name)],limit=1)
        if not registration_sudo:
            raise NotFound()

        if registration_sudo.state  in ['draft', 'done']:
            registration_sudo.action_cancel_without_refund()
        elif registration_sudo.state  == 'invoiced':
            registration_sudo.action_refund_and_cancel()


        return request.redirect('/my/cricket_box/registrations')



    @route(['/my/cricket_box/pay/<string:name>'], type='http', auth='user', methods=['GET'], csrf=True)
    def confirm_booking(self, **kwargs):
        """Function for confirming the box selection and creating an invoice."""

        # get registration name
        registration_name = kwargs.get('name')
        if not registration_name:
            raise NotFound("Registration name is required.")

        # search for the registration record
        registration_sudo = request.env['cricket.box.registration'].sudo().search([('name', '=', registration_name)], limit=1)
        if not registration_sudo:
            raise NotFound("Registration record not found.")

        box_id = registration_sudo.box_id
        if not box_id:
            raise NotFound("Box ID is required.")

        cricket_box = request.env['cricket.box'].sudo().browse(int(box_id))
        if not cricket_box.exists():
            raise NotFound("Cricket box not found.")

        product = request.env.ref('cricket_box_booking_management.product_1')
        if not product:
            raise NotFound("Product not found.")

        invoice = request.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': request.env.user.partner_id.id,
            'invoice_origin': 'Cricket Box Booking',
            'box_ticket_id': registration_sudo.id,
            'is_booking_invoice': True,
            'box_id': registration_sudo.box_id.id,
            'invoice_date': fields.Date.today(),
            'state': 'draft',
            'invoice_line_ids': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'quantity': (len(registration_sudo.time_slot_id.ids)),
                'price_unit': cricket_box.price,
            })],
        })

        if invoice:
            invoice.sudo().action_post()

            registration_sudo.write({'state': 'invoiced'})

        access_token = invoice._portal_ensure_token()

        params = {'access_token': access_token,
            'payment_method_id': kwargs.get('payment_method_id')}
        return request.redirect(f'/my/invoices/{invoice.id}?{url_encode(params)}')




    @http.route('/my/cricket_box/register/<int:box_id>', type='http', auth="user", website=True)
    def cricket_box_registration(self, box_id, **kwargs):
        # Fetch cricket box and related data
        cricket_box = request.env['cricket.box'].sudo().browse(box_id)
        selected_date = kwargs.get('date')
        # selected_name = kwargs.get('name')

        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        available_time_slots = []

        if selected_date:
            select_date = cricket_box.select_dates.filtered(
                lambda d: d.date == selected_date  )


            if select_date:
                available_time_slots = select_date.available_time_slots_ids

        if request.httprequest.method == 'POST':
            action = kwargs.get('action')
            if  action == 'check':
                return request.render('cricket_box_booking_management.portal_cricket_box_registration', {
                    'cricket_box': cricket_box,
                    'select_dates': cricket_box.select_dates,
                    'available_time_slots': available_time_slots,
                    'selected_date': selected_date,
                    'error': None,
                })
            missing_fields = []
            if not selected_date:
                missing_fields.append('Date')
            if not kwargs.get('time_slot_ids'):
                missing_fields.append('Time-Slot')

            if missing_fields:
                return request.render('cricket_box_booking_management.portal_cricket_box_registration', {
                    'cricket_box': cricket_box,
                    'select_dates': cricket_box.select_dates,
                    'available_time_slots': available_time_slots,
                    'selected_date': selected_date,
                    'error': f"Please Select {', '.join(missing_fields)}..!!",
                })

            time_slot_ids = request.httprequest.form.getlist('time_slot_ids')

            registration = request.env['cricket.box.registration'].sudo().create({
                'partner_id': request.env.user.partner_id.id,
                'box_id': box_id,
                'date': selected_date,
                'time_slot_id': [(6, 0, list(map(int, time_slot_ids)))],
                'active': True,
                'state': 'draft'
            })
            # print(f"Registration Created: {registration}")
            registration_find = request.env['cricket.box.registration'].sudo().search([('box_id', '=', box_id),('date', '=' , selected_date),('time_slot_id', 'in', time_slot_ids),('state', '=', 'draft')],limit = 1)
            return request.redirect(f'/my/cricket_box/registrations?name={registration_find.name}')

        return request.render('cricket_box_booking_management.portal_cricket_box_registration', {
            'cricket_box': cricket_box,
            'select_dates': cricket_box.select_dates,
            'available_time_slots': available_time_slots,
            'selected_date': selected_date,
            'error': None,
        })
