# -*- coding: utf-8 -*-

from odoo import models, fields


class BidEvaluationWizard(models.TransientModel):
    _name = 'bid.evaluation.wizard'

    selection_justification = fields.Text(string='Justification for Selection')

    def set_bid_as_winner(self):
        self.ensure_one()
        bid_evaluation_id = self.env['bid.evaluation'].browse(self.env.context.get('active_id'))
        bid_evaluation_id.write({
            'selection_justification': self.selection_justification,
            'winning_bid': True})
        self.env['bid.evaluation'].search([('purchase_requisition_id', '=', bid_evaluation_id.purchase_requisition_id.id)]).write({
            'selection_complete': True})
        bid_evaluation_id.purchase_requisition_id.write({
            'selected_bid_id': bid_evaluation_id.po_id.id,
            'selection_justification': self.selection_justification,
            })
        
