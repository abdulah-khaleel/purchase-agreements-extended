# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError



class BidEvaluation(models.Model):
    _name = 'bid.evaluation'
    _description = 'Bid/Quotation Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Title")
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Purchase Requisition")
    po_id = fields.Many2one('purchase.order', 'RFQ')
    partner_id = fields.Many2one('res.partner',  string="Vendor")
    deadline = fields.Date(string="Deadline", default = lambda self: self.po_id.date_order)
    evaluation_guidelines = fields.Text('Evaluation Guidelines')
    score_limit = fields.Integer('Highest Score')
    score_avg = fields.Float('Average Score', compute="_compute_score_avg")
    notes = fields.Text('Notes')
    checklist_item_ids = fields.One2many('bid.evaluation.checklist','bid_evaluation_id', string="Evaluation Checklist")
    question_ids = fields.One2many('bid.evaluation.question', 'bid_evaluation_id', string="Bid Evaluation Questions")
    bid_approver_ids = fields.Many2many('bid.panel.members', string="Panel Members")
    winning_bid = fields.Boolean(string="Winning Bid", readonly=True, default=False)
    selection_complete = fields.Boolean(string="Selection Complete", default=False)
    selection_justification = fields.Text('Selection Justification')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], default='draft', string="Status", track_visibility=True)
    user_status = fields.Selection([
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ], compute="_compute_user_status")
    edit_questions = fields.Selection([
        ('allowed', 'Allowed'),
        ('not_allowed', 'Not Allowed'),
        ], compute="_check_questions_edit_access")
    
    
    def get_panel_member_activity(self,user):
        domain = [
            ('res_model', '=', 'bid.evaluation'),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', self.env.ref('ak_purchase_agreement_panel.mail_bid_panel_member_evaluation_notification').id),
            ('user_id', '=', user.id)
        ]
        activity = self.env['mail.activity'].search(domain,limit=1)
        return activity
        
    
    def create_activity(self):
        self.ensure_one()
        for member in self.bid_approver_ids.user_id:
                    self.activity_schedule('ak_purchase_agreement_panel.mail_bid_panel_member_evaluation_notification',
                        date_deadline=self.deadline or self.po_id.date_order, 
                        user_id = member.id, 
                        note=f"The Bid evaluation/scoring for the purchase agreement and vendor ref: {self.name} has been created and is pending your review.")
    
    def cancel_evaluation(self):
        domain = [
            ('res_model', '=', 'bid.evaluation'),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', self.env.ref('ak_purchase_agreement_panel.mail_bid_panel_member_evaluation_notification').id),
        ]
        activitie = self.env['mail.activity'].search(domain)
        activitie.sudo().unlink()
        self.write({'state': 'cancel'})
        for approval in self.bid_approver_ids:
            if approval.user_id.id == self.env.user.id:
                approval.write({
                    'review_state': 'cancel',
                    'approval_date': fields.Datetime.now(),
                    })
            

    def reset_to_draft(self):
        self.write({'state': 'draft'})
        # reset approval ids status to 'pending':
        self.bid_approver_ids.write({
            'review_state': 'pending',
            'approval_date': False
            })

    
    def submit_evaluation(self):
        self.ensure_one()
        for question in self.question_ids:
            if question.score == 0:
                raise ValidationError(
                    _(f"Scores should be between 1 and {self.score_limit}. Please make sure that all factors are scored properly and try again."))
        self.create_activity()
        self.write({'state': 'to_approve'})
        for approval in self.bid_approver_ids:
            approval.write({
                'review_state': 'pending'
                })

    def approve_evaluation(self):
        for approver in self.bid_approver_ids:
            if approver.user_id.id == self.env.user.id:
                approver.write({
                    'review_state': 'approved',
                    'approval_date': fields.Datetime.now(),
                    })
                self.sudo().get_panel_member_activity(user=self.env.user).unlink()
                self.message_post(body='Evaluation reviewed and approved.')

            if not 'pending' in self.bid_approver_ids.mapped('review_state'):
                self.write({'state': 'done'})

    def set_as_winner(self):
        self.ensure_one()
        self.write({'winning_bid': True})


    def get_checklist_status(self, status):
        if status == 'yes':
            return 'Yes'
        else:
            return 'No'

    def unlink(self):
        if self.state != 'cancel':
            raise UserError(
                        'You can only delete evaluation records that are in a cancelled state.'
                    )
        # update related purchase order:
        self.mapped('po_id').write({'has_evaluation': False})
        return super(BidEvaluation, self).unlink()
    
    @api.depends('question_ids.score')
    def _compute_score_avg(self):
        for rec in self:
            scores = rec.question_ids.mapped('score')
            if len(scores) != 0:
                rec.score_avg = sum(scores) / len(scores)
            else:
                rec.score_avg = 0

    
    @api.depends('question_ids.name')
    def _check_questions_edit_access(self):
        for eval in self:
            if self.env.user.has_group('purchase.group_purchase_user'):
                eval.edit_questions = 'allowed'
            else:
                eval.edit_questions = 'not_allowed'
            # approval.user_status = approval.bid_approver_ids.filtered(lambda approver: approver.user_id == self.env.user).review_state


    @api.depends('bid_approver_ids.review_state')
    def _compute_user_status(self):
        for approval in self:
            approval.user_status = approval.bid_approver_ids.filtered(lambda approver: approver.user_id == self.env.user).review_state

    
    @api.constrains('question_ids.score')
    def _check_max_score(self):
        for score in self.question_ids.score:
            if score > self.bid_evaluation_id.score_limit:
                raise ValidationError(
                    _(f"The maximum score limit you can provide on each question/factor is {self.bid_evaluation_id.score_limit}."))

class BidEvaluationQuestion(models.Model):
    _name = 'bid.evaluation.question'
    _description = 'Bid Evaluation Question'

    name = fields.Char(string="Question / Factor")
    score = fields.Integer('Score')
    remarks = fields.Text('Remarks')
    bid_evaluation_id = fields.Many2one('bid.evaluation', string="Bid Evaluation")

    @api.constrains('score')
    def _check_max_score(self):
        if self.bid_evaluation_id.score_limit:
            if self.score > self.bid_evaluation_id.score_limit:
                raise ValidationError(
                    _(f"The maximum score limit you can provide on each question/factor is {self.bid_evaluation_id.score_limit}."))

class BidEvaluationChecklist(models.Model):
    _name = 'bid.evaluation.checklist'
    _description = 'Bid Evaluation Checklist'

    name = fields.Char(string="Item")
    item_clear = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], string="Available", required=True)
    bid_evaluation_id = fields.Many2one('bid.evaluation', string="Bid Evaluation")


class BidPanelMembers(models.Model):
    _name = 'bid.panel.members'
    _description = 'Bid EValuation Panel'

    bid_evaluation_id = fields.Many2one('bid.evaluation', string="Bid Evaluation")
    user_id = fields.Many2one('res.users', string="Panel Member", required=True)
    user_email = fields.Char('Email', related='user_id.login')
    review_state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ], default='pending', string="Review Status")
    approval_date = fields.Datetime('Approval Date', readonly=True)

 
class BidEvaluationWizard(models.TransientModel):
    _name = 'bid.evaluation.wizard'

    selection_justification = fields.Text(string='Justification for Selection')

    def set_bid_as_winner(self):
        self.ensure_one()
        bid_evaluation_id = self.env['bid.evaluation'].browse(self.env.context.get('active_id'))
        bid_evaluation_ids_state = self.env['bid.evaluation'].search([('purchase_requisition_id', '=', bid_evaluation_id.purchase_requisition_id.id)]).mapped('state')
        # if 'cancel' in bid_evaluation_ids_state or ''
        #     raise ValidationError(
        #         _(f"You cannot select a winner for a cancelled bid."))
        #     raise ValidationError(
        #         _(f"You cannot set a bid as winner because the evaluation is already done."))

        
        bid_evaluation_id.write({
            'selection_justification': self.selection_justification,
            'winning_bid': True})
        self.env['bid.evaluation'].search([('purchase_requisition_id', '=', bid_evaluation_id.purchase_requisition_id.id)]).write({
            'selection_complete': True})
        bid_evaluation_id.purchase_requisition_id.write({
            'selected_bid_id': bid_evaluation_id.po_id.id,
            'selection_justification': self.selection_justification,
            })
        
