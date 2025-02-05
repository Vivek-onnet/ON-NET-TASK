# -*- coding: utf-8 -*-
{
    'name': "Admission",
    'summary': "Student Admission For School",
    'description': "This is Student Admission model.",
    'author': "Vivek Vaghela",
    'version': '0.1',
    'depends': ['base','account'],
    'data': [
        'views/registration_view.xml',
        'security/ir.model.access.csv',
        'data/fees.xml',

            ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
