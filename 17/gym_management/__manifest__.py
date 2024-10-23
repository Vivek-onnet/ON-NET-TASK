# -*- coding: utf-8 -*-
{
    'name': "Gym Management",

    'summary': "Gym Management System",

    'description': "This is Gym Management System",

    'author': "Vivek Vaghela",
    # 'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    # 'category': 'Uncategorized',
    'version': '0.1',
    'sequence': -100,

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product','hr_attendance','account','membership'],

    # always loaded
    'data': [
        'security/gym_security_access_data.xml',
        'security/ir.model.access.csv',
        'wizard/membership_invoice.xml',
        'demo/demo.xml',
        'demo/demo_diet_plan.xml',
        'demo/days_demo.xml',
        'demo/membership_demo.xml',
        'demo/workout_demo.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/membership.xml',
        'views/exercise.xml',
        'views/exercise_print.xml',
        'views/workout_plan.xml',
        'views/workout_plan_report.xml',
        'views/diet_plan.xml',
        'views/diet_plan_report.xml',
        'views/attendance.xml',
        'views/gym_invoices.xml',
        'views/gym_member_menu.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
