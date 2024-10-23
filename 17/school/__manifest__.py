# -*- coding: utf-8 -*-

{
    'name': "School Admin",
    'category': 'Administration',
    'version': '1.1',
    'sequence': -100,
    'summary': "School Management System",
    'author': "Vivek Vaghela",
    'description': "This is School Management System",
    'depends': ['base', 'sale'],
    'data': [
        'data/school_data.xml',
        "data/delete_data.xml",
        # 'security/ir.model.access.csv',
        'security/security_access_data.xml',
        'views/school_view.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
