from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
import base64
from odoo.http import request


class StudentMenu(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        rtn = super(StudentMenu, self)._prepare_home_portal_values(counters)
        rtn['student_counts'] = request.env['school.student'].search_count([])
        print("counters:", rtn['student_counts'])
        return rtn

    @http.route('/my/students', website=True, auth='user')
    def student_menu_list(self, **kw):
        students = request.env['school.student'].sudo().search([])
        return request.render("school_student.portal_students_list",
                              {'students': students, 'page_name': 'student_list_view'})

    @http.route('/my/students/<model("school.student"):student_id>', type='http', website=True, auth='public')
    def student_menu_form(self, student_id, **kw):
        vals = {'student': student_id, 'page_name': 'student_form_view'}
        return request.render("school_student.portal_students_form", vals)

    @http.route('/my/students/print/<model("school.student"):student_id>', type='http', auth='user', website=True)
    def student_report_print(self, student_id, **kw):
        print("hello//////", student_id)
        return self._show_report(model=student_id, report_type='pdf',
                                 report_ref='school_student.student_card_pdf_report', download=True)

    @http.route('/my/students/add',type='http', website=True, auth='user')
    def student_register(self, **kw):
        school_list = request.env['school.profile'].search([])
        if request.httprequest.method == 'POST':
            print(kw)
            request.env['school.student'].create({"name": kw.get('name'), "bdate": kw.get('bdate'), "school_id": int(kw.get('school'))})
        else:
            print("GET")

        return request.render("school_student.student_registration_form", {'schools' : school_list ,  'page_name': 'student_registration_view'})
