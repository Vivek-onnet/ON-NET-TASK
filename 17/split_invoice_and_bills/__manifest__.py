# -*- coding: utf-8 -*-
{
    'name': "TEST Split Invoice and Bills",

    'summary': "Effortlessly split invoices and bills.",

    'description': """Long description of module's purpose""",

    'author': "VPerfect CS",
    # 'website': "https://vpcscloud.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',
    'sequence': -100,

    # any module necessary for this one to work correctly
    'depends': ['account'],

    'images': [
        'static/description/temp.gif',
    ],

    # always loaded
    'data': [
        # 'security/split_bill_security.xml',
        'security/ir.model.access.csv',
        'wizard/split_bills_invoice_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
    'installable': True,
    'license': 'LGPL-3'

}

