# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_playsms_http", "SMS PlaySMS http")],
        ondelete={"sms_playsms_http": "cascade"},
    )
    sms_playsms_http_endpoint = fields.Char(string="PlaySMS Endpoint", default='http://localhost/playsms/index.php?app=ws')
    sms_playsms_http_webtoken = fields.Char(string="Webtoken")
    sms_playsms_http_login = fields.Char(string="Login")
    sms_playsms_http_password = fields.Char(string="Password")
    sms_playsms_http_from = fields.Char(string="Expeditor Number")

    def _get_service_from_provider(self):
        if self.provider == "sms_playsms_http":
            return "sms"

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_playsms_http_endpoint": {},
                "sms_playsms_http_webtoken": {},
                "sms_playsms_http_login": {},
                "sms_playsms_http_password": {},
                "sms_playsms_http_from": {},
            }
        )
        return res
