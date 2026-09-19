from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_depreciation_ids = fields.One2many('custom.account.asset.depreciation.line', 'move_id',
                                             string='Assets Depreciation Lines')

    def button_cancel(self):
        for move in self:
            for line in move.asset_depreciation_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    def action_post(self):
        # Depreciation updates ran before core posting in the separate extensions.
        for move in self:
            for depreciation_line in move.asset_depreciation_ids:
                depreciation_line.post_lines_and_close_asset()
        result = super().action_post()
        for move in self:
            context = dict(self.env.context)
            context.pop('default_type', None)
            for line in move.invoice_line_ids:
                line.with_context(context).asset_create()
        return result

    asset_ids = fields.One2many(
        'custom.account.asset.asset', 'invoice_id', string="Assets"
    )

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for move in self:
            if any(asset_id.state != 'draft' for asset_id in move.asset_ids):
                raise ValidationError(_(
                    'You cannot reset to draft for an entry having a posted asset'))
            if move.asset_ids:
                move.asset_ids.sudo().write({'active': False})
                for asset in move.asset_ids:
                    asset.sudo().message_post(body=_("Vendor bill cancelled."))
        return res

    @api.model
    def _refund_cleanup_lines(self, lines):
        result = super(AccountMove, self)._refund_cleanup_lines(lines)
        for i, line in enumerate(lines):
            for name, field in line._fields.items():
                if name == 'asset_category_id':
                    result[i][2][name] = False
                    break
        return result

    def action_cancel(self):
        res = super(AccountMove, self).action_cancel()
        assets = self.env['custom.account.asset.asset'].sudo().search(
            [('invoice_id', 'in', self.ids)])
        if assets:
            assets.sudo().write({'active': False})
            for asset in assets:
                asset.sudo().message_post(body=_("Vendor bill cancelled."))
        return res

    @api.model
    def _get_invoice_in_payment_state(self):
        return 'in_payment'
