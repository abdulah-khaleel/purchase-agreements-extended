# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BidEvaluation(models.Model):
    _name = 'bid.evaluation'
    _description = 'Bid/Quotation Evaluation'

    name = fields.Char(string="Panel Title", required=True)
    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Purchase Requisition")
