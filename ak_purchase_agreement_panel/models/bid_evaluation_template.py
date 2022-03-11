# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BidEvaluationTemplate(models.Model):
    _name = 'bid.evaluation.template'
    _description = 'Bid/Quotation Evaluation Template'

    name = fields.Char(string="Evaluation Template Name", required=True)
    evaluation_approach = fields.Boolean('Evaluation Approach')
    scorable = fields.Boolean('Scorable?')
    score_limit = fields.Integer('Maximum Score')
    checklist_item_ids = fields.One2many('bid.template.checklist', 'evaluation_template_id',string="Bid Checklist")
    question_ids = fields.One2many('bid.template.question', 'evaluation_template_id',string="Bid Evaluation Questions")


class BidTemplateQuestion(models.Model):
    _name = 'bid.template.question'
    _description = ' Bid Template Question'

    name = fields.Char(string="Question/Factor", required=True)
    evaluation_template_id = fields.Many2one('bid.evaluation.template')

    
class BidTemplateChecklist(models.Model):
    _name = 'bid.template.checklist'
    _description = ' Bid Template Checklist'

    name = fields.Char(string="Item", required=True)
    evaluation_template_id = fields.Many2one('bid.evaluation.template')