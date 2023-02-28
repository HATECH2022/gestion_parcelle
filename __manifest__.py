# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Gestion de Parcelle",
    "summary": "Gestion de Parcelle",
    "author": "HATECH",
    "website": "www.hornafricatech.com",
    "category": "Custom Application",
    "version": "14.0",
    "license": "AGPL-3",
    "depends": ['base', 'mail', 'sale','account'],
    "data": [
        # 'data/courrier_data.xml',
        # 'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/main_menu_view.xml',
        'views/gestion_parcelle.xml',
        'views/zone_parcelle.xml',
        'views/projet_parcelle.xml',
        'views/analyse_parcelle.xml',
        'views/parcelle_sale_order.xml',
        'report/report_fiche_renseignement.xml',
       	'views/account_view.xml',
        # 'views/email_template.xml',

    ],
    'images': [
        'static/description/parcelle.png',
    ],

    'license': 'AGPL-3',
    'installable': True,
    "application": True,
    "development_status": "Beta",
    "maintainers": ["Horn Africa Technology"],
}
