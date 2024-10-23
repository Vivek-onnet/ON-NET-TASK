from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request
class StudentWebsite(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        rtn = super(StudentWebsite, self)._prepare_home_portal_values(counters)
        rtn['student_counts'] = request.env['school.student'].search_count([])
        print("counters_ok:",rtn['student_counts'])
        return rtn
class SchoolStudent(http.Controller):
    @http.route('/my/school_student', website=True, auth='user')
    def schoolstudent(self, **kw):
        student = request.env['school.student'].sudo().search([])
        return request.render('school_student.student_web_template', {
            'model_school_student': student
        })



