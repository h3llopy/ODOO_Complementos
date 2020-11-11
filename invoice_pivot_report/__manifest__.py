# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Pivot Invoice Views',
    'version': '12.0.0',
    'category': 'Reporting',
    'summary': 'Invoice Pivot Views',
    'author': '',
    "website": "",
    'depends': [
        'account',
        'date_range',
        'report_xlsx',
        'xml_generation',
    ],
    'data': [
        'view/account_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': '',
}
