# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    has_evaluation = fields.Boolean(string='Has Evaluation', default=False, copy=False)
    evaluation_count = fields.Integer(compute="_compute_evaluations_count")

    def get_question_ids(self):
        questions_list = []
        for question in self.requisition_id.eval_template_id.question_ids:
            questions_list.append((0, 0, {'name': question.name}))
        return questions_list

    def get_panel_members(self):
        members_list = []
        for member in self.requisition_id.panel_id.member_ids:
            members_list.append((0, 0, {'user_id': member.id, 'review_state': 'pending'}))
        return members_list

    def get_checklist_item_ids(self):
        checklist_list = []
        for item in self.requisition_id.eval_template_id.checklist_item_ids:
            checklist_list.append((0, 0, {'name': item.name, 'item_clear': 'no'}))
        return checklist_list
    
    def get_bid_evaluation_record(self):
        self.ensure_one()
        bid_evaluation_record = self.env['bid.evaluation'].search([('po_id', '=', self.id)])
        if bid_evaluation_record:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Bid Evaluation',
                'view_mode': 'form',
                'res_model': 'bid.evaluation',
                'res_id': bid_evaluation_record.id,
                'domain': [('po_id', '=', self.id)],
            }
     


    def create_bid_evaluation(self):
        if not self.requisition_id.eval_template_id or not self.requisition_id.panel_id:
            raise UserError(_("Please make sure an evaluation template and a purchase committee have been set on the requisition of this bid."))
        bid_evaluation_record = self.env['bid.evaluation'].sudo().create({
            'name': f'Bid Evaluation - {self.requisition_id.name} - {self.partner_id.name}',
            'po_id': self.id,
            'purchase_requisition_id': self.requisition_id.id,
            'partner_id': self.partner_id.id,
            'deadline': self.date_order,
            'evaluation_guidelines': self.requisition_id.evaluation_guidelines,
            'score_limit': self.requisition_id.eval_template_id.score_limit,
            'checklist_item_ids': self.get_checklist_item_ids(),
            'question_ids': self.get_question_ids()
          })
        # bid_evaluation_record = self.env['bid.evaluation'].search([('po_id', '=', self.id)])
        bid_evaluation_record.sudo().write({
            'bid_approver_ids': self.get_panel_members()
        })
        self.write({'has_evaluation': True})
        return self.get_bid_evaluation_record()

    def _compute_evaluations_count(self):
        BidEvaluations = self.env['bid.evaluation']
        self.evaluation_count = BidEvaluations.search_count([('po_id', '=', self.id)])
