# -*- coding: utf-8 -*-
################################################################################# 
#
#    Author: Abdullah Khalil. Copyrights (C) 2021-TODAY reserved. 
#
#    You may use this app as per the rules outlined in the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3. 
#    See <http://www.gnu.org/licenses/> for more detials.
#
################################################################################# 

{
    'name': "Purchase Agreement Panels",   
    'summary': "Panel Members can evaluate quotations and participate in bid selection",   
    'description': """
        This app extends on the purchase agreement workflow by allowing you to setup purchase 
        panels, and invite panel members to participate in the bids evaluation 
        process. The app also allows setting up evaluation forms that can be selected for a
         particular purchase agreement.  
    """,   
    'author': "Abdullah Khalil",
    'website': "https://github.com/abdulah-khaleel",
    'category': 'Purchase',
    'version': '14.0.0.0',
     "license": "LGPL-3",
    'depends': ['base','purchase','purchase_requisition'],
    'data': [
        'security/purchase_panel_security.xml',
        'security/ir.model.access.csv',
        'views/purchase_panel.xml',
        'views/purchase_requisition.xml',
        'views/purchase_requisition_type.xml',
        'views/bid_evaluation_template.xml',
        'wizard/bid_evaluation_wizard.xml',
        'views/bid_evaluation.xml',
        'views/purchase_order.xml',
        'reports/bid_evaluation_report.xml',
        'reports/bids_checklist_summary.xml',
        'reports/bids_evaluation_summary.xml',
        'reports/bids_comparative_report.xml',
    ],
    # 'images': ["static/description/banner-v15.png"],
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
} 
