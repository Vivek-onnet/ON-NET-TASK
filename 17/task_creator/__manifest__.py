# -*- coding: utf-8 -*-
{
    'name': "Task Creator",
    'summary': "Task Creator For Project",
    'description': "This is task creator.",
    'author': "Vivek Vaghela",
    'version': '0.1',
    'sequence': -100,
    'depends': ['sale','sale_project','product'],
    'data': [
        'views/task_creator_view.xml',
            ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
