# -*- coding: utf-8 -*-
{
    'name': "VPCS Split Invoice and Bills",
    'summary': "Effortlessly split invoices and bills.",
    'description': """Long description of module's purpose""",
    'author': "VPerfect CS",
    'category': 'account',
    'version': '0.1',
    "sequence": 2,
    'depends': ['account'],
    'images': ['static/description/temp.gif',],
    'data': [
        'security/split_bill_security.xml',
        'security/ir.model.access.csv',
        'wizard/split_bills_invoice_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}

