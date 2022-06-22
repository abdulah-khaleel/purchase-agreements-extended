# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    enable_comittee_evaluation = fields.Boolean('Enable Purchase Committee Evaluation', help="hell world")