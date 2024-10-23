# -*- coding: utf-8 -*-
{
    'name': "School Student",
    'sequence': -100,
    'category': 'Portal',
    'version': '1.1',

    'summary': "Student Management System",
    'author': "Vivek Vaghela",
    'description': "This is Student Management System",
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'school', 'hospital', 'web','portal'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'data/student_data.xml',
        "data/school.profile.csv",
        "data/school.student.csv",
        'data/hobby.csv',
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/student_fees_update_wizard_view.xml',
        'report/student_card_templates.xml',
        'report/webtemp.xml',
        'report/website_stu.xml',

    ],
    # only loaded in demonstration mode
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {

        'web.assets_frontend': [
            '/school_student/static/css/style.css',

        ],
    }

}
