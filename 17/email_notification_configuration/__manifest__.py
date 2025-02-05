# -*- coding: utf-8 -*-
{
    'name': "Email Notification Configuration",
    'summary': "Email Notification Configuration For Due Inovice",
    'description': "This is Email Notification Configuration.",
    'author': "Vivek Vaghela",
    'version': '0.1',
    'depends': ['base','account' ,'stock'],
    'data': [
        'views/email_notification_configuration_settings_view.xml',
        'data/email_template.xml'
            ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3'
}
