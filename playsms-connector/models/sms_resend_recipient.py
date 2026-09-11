# -*- coding: utf-8 -*-
# Copyright 2024 Walther Barnett (original 17.0 author)
# Copyright 2026 Entuura (Asia) Limited — 18.0 port
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SmsResendRecipient(models.TransientModel):
    _inherit = "sms.resend.recipient"

    failure_reason = fields.Text(
        related="notification_id.failure_reason",
        string="Error Description",
        related_sudo=True,
        readonly=True,
    )
