from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fiscalyear_last_day = fields.Integer(
        related='company_id.fiscalyear_last_day', readonly=False
    )

    fiscalyear_last_month = fields.Selection(
        related='company_id.fiscalyear_last_month', readonly=False
    )

    tax_lock_date = fields.Date(
        related='company_id.hard_lock_date', readonly=False
    )

    sale_lock_date = fields.Date(
        related='company_id.hard_lock_date', readonly=False
    )

    purchase_lock_date = fields.Date(
        related='company_id.hard_lock_date', readonly=False
    )

    hard_lock_date = fields.Date(
        related='company_id.hard_lock_date', readonly=False
    )

    fiscalyear_lock_date = fields.Date(
        related='company_id.fiscalyear_lock_date', readonly=False
    )

    group_fiscal_year = fields.Boolean(
        string='Fiscal Years', implied_group='custom_accounting_kit.group_fiscal_year'
    )

    def open_followup_level_form(self):
        res_ids = self.env['custom.followup.followup'].search([], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Follow-up Levels',
            'res_model': 'custom.followup.followup',
            'res_id': res_ids and res_ids.id or False,
            'view_mode': 'form,list',
        }

    anglo_saxon_accounting = fields.Boolean(
        related="company_id.anglo_saxon_accounting",
        readonly=False, string="Use anglo-saxon accounting",
        help="Record the cost of a good as an expense when this good is invoiced to a final customer."
    )
