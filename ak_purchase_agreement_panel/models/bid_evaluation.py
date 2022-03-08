# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class BidEvaluation(models.Model):
    _name = 'bid.evaluation'
    _description = 'Bid/Quotation Evaluation'

    name = fields.Char(string="Title")
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Purchase Requisition")
    po_id = fields.Many2one('purchase.order', 'RFQ')
    partner_id = fields.Many2one('res.partner',  string="Vendor")
    evaluation_approach = fields.Boolean('Allow Evaluation Approach')
    evaluation_guidelines = fields.Text('Evaluation Guidelines')
    evaluation_approach_description = fields.Text('Evaluation Approach')
    score_limit = fields.Integer('Highest Score')
    notes = fields.Text('Notes')
    question_ids = fields.One2many('bid.evaluation.question', 'bid_evaluation_id', string="Bid Evaluation Questions")
    bid_approver_ids = fields.Many2many('bid.panel.members', string="Panel Members")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('done', 'Done'),
        ], default='draft', string="Status")
    user_status = fields.Selection([
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ], compute="_compute_user_status")

    def submit_evaluation(self):
        self.ensure_one()
        for question in self.question_ids:
            if question.score == 0:
                raise ValidationError(
                    _(f"Scores should be between 1 and {self.score_limit}. Please make sure that all factors are scored properly and try again."))
        self.write({'state': 'to_approve'})

    def approve_evaluation(self):
        for approver in self.bid_approver_ids:
            if approver.user_id.id == self.env.user.id:
                approver.write({'review_state': 'approved'})
            if not 'pending' in self.bid_approver_ids.mapped('review_state'):
                self.write({'state': 'done'})
            else:
                print('still approvals to go..')
    
    @api.depends('bid_approver_ids.review_state')
    def _compute_user_status(self):
        for approval in self:
            approval.user_status = approval.bid_approver_ids.filtered(lambda approver: approver.user_id == self.env.user).review_state

    
    @api.constrains('question_ids.score')
    def _check_max_score(self):
        for score in self.question_ids.score:
            if score == 0:
                raise ValidationError(
                    _(f"The maximum score limit you can provide on each question/factor is {self.bid_evaluation_id.score_limit}."))
            else:
                print('all good.')

class BidEvaluationQuestion(models.Model):
    _name = 'bid.evaluation.question'
    _description = 'Bid Evaluation Question'

    name = fields.Char(string="Question / Factor", readonly=True)
    score = fields.Integer('Score')
    remarks = fields.Text('Remarks')
    bid_evaluation_id = fields.Many2one('bid.evaluation', string="Bid Evaluation")

    @api.constrains('score')
    def _check_max_score(self):
        if self.bid_evaluation_id.score_limit:
            if self.score > self.bid_evaluation_id.score_limit:
                raise ValidationError(
                    _(f"The maximum score limit you can provide on each question/factor is {self.bid_evaluation_id.score_limit}."))
        else:
            print('no score limit dfeined ..................')

class BidPanelMembers(models.Model):
    _name = 'bid.panel.members'
    _description = 'Bid EValuation Panel'

    bid_evaluation_id = fields.Many2one('bid.evaluation', string="Bid Evaluation")
    user_id = fields.Many2one('res.users', string="Panel Member", required=True)
    user_email = fields.Char('Email', related='user_id.login')
    review_state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ], default='pending', string="Review Status")



    
