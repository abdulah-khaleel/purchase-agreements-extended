# -*- coding: utf-8 -*-

from tabnanny import check
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    panel_id = fields.Many2one('purchase.panel', string="Purchase Comittee")
    enable_panel = fields.Boolean('Enable Panel Committee', compute='_check_for_purchase_panel')
    eval_template_id = fields.Many2one('bid.evaluation.template', string="Bid Evaluation Template")

    def get_bid_evaluations(self):
        evaluation_records = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', self.id)])
        return evaluation_records

    def get_checklist_summary_titles(self):

        evaluation_records = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', self.id)])
        return sorted(list(set(evaluation_records.mapped('checklist_item_ids.name'))))
    
    def get_checklist_summary_lines(self):

        evaluation_records = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', self.id)])
        checklist_item_names = sorted(list(set(evaluation_records.mapped('checklist_item_ids.name'))))
        
        checklist_l = []
        for rec in evaluation_records:
            bidder_list = []
            bidder_list.append(rec.partner_id.name)
            partner_dict = {}
            if len(rec.checklist_item_ids) == 0:
                for name in checklist_item_names:
                    partner_dict[name] = 'N/A' 
            else:
                for checklist_title in checklist_item_names:
                    for line in rec.checklist_item_ids:
                        if line.name == checklist_title:
                            partner_dict[line.name] = line.item_clear
            for title in checklist_item_names:
                if title not in partner_dict:
                    partner_dict[title] = 'N/A'

            # sorted_partner_dict = {}
            sorted_partner_dict = {key: value for key, value in sorted(partner_dict.items())}

            bidder_list.append(sorted_partner_dict)
            checklist_l.append(bidder_list)

        return checklist_l
    
    def get_evaluation_questions(self):

        evaluation_records = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', self.id)])
        return sorted(list(set(evaluation_records.mapped('question_ids.name'))))

    def get_evaluation_summary_lines(self):

        evaluation_records = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', self.id)])
        question_titles = sorted(list(set(evaluation_records.mapped('question_ids.name'))))
        
        eval_list = []
        for rec in evaluation_records:
            bidder_list = []
            bidder_list.append(rec.partner_id.name)
            partner_dict = {}
            if len(rec.question_ids) == 0:
                for name in question_titles:
                    partner_dict[name] = 'N/A'
            else:
                for question in question_titles:
                    for line in rec.question_ids:
                        if line.name == question:
                            partner_dict[line.name] = line.score
            for title in question_titles:
                if title not in partner_dict:
                    partner_dict[title] = 'n/a - 2'

            # sorted_partner_dict = {}
            sorted_partner_dict = {key: value for key, value in sorted(partner_dict.items())}

            bidder_list.append(sorted_partner_dict)
            eval_list.append(bidder_list)

        return eval_list
    
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
     