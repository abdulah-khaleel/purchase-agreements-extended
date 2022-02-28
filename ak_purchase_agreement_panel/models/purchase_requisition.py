# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    panel_id = fields.Many2one('purchase.panel', string="Purchase Comittee")
    enable_panel = fields.Boolean('Enable Panel Committee', compute='_check_for_purchase_panel')

   

    def action_done(self):
        self.activity_unlink(['ak_purchase_agreement_panel.mail_purchase_panel_member_notification'])
        return super(PurchaseRequisition,self).action_done()

    
    def action_open(self):
        if self.type_id.enable_comittee_evaluation:
            if self.panel_id:
                for user in self.panel_id.member_ids:
                    self.activity_schedule('ak_purchase_agreement_panel.mail_purchase_panel_member_notification',
                        date_deadline=self.date_end, 
                        user_id = user.id, 
                        note=f"""As part of the purchae comittee for the agreement: {self.name}, you 
                        are requested to navigate to the purchase agreement above and complete the evaluation for each of the bids recieved.""")
            # else:
            #     raise ValidationError(_('You need to select a Purchase Comittee before validating this agreement.'))
        return super(PurchaseRequisition,self).action_open()

    @api.depends('type_id')
    def _check_for_purchase_panel(self):
        if self.type_id.enable_comittee_evaluation:
            self.write({
                'enable_panel': True,
                })
        else:
            self.write({
                    'enable_panel': False,
                    })
    


 

