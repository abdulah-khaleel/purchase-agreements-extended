# -*- coding: utf-8 -*-

from distutils.command.build_scripts import first_line_re
from odoo import models, fields, api, _


class PurchasePanel(models.Model):
    _name = 'purchase.panel'
    _description = 'Purchase Panel'

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string="Panel Title", required=True)
    member_ids = fields.Many2many('res.users', string="Panel Members")

    def write(self, values):
        res = super(PurchasePanel, self).write(values)
        for member in self.member_ids:
            if not member.has_group('ak_purchase_agreement_panel.group_purchase_panel_member'):
                member.write({'groups_id': [(4, self.env.ref('ak_purchase_agreement_panel.group_purchase_panel_member').id)]})
        return res
        

