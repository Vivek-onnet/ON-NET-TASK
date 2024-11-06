# -*- coding: utf-8 -*-
{
    'name': "Gym",

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
        # 'security/gym_security_access_data.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/data_diet_plan.xml',
        'data/days_data.xml',
        'data/membership_data.xml',
        'data/workout_data.xml',
        'views/gym_management.xml',
        'views/gym_member_menu.xml',
        'wizard/membership_invoice.xml',
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
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
