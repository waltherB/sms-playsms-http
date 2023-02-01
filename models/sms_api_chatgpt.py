import requests

from odoo import _, api, models
from odoo.exceptions import UserError

PLAYSMS_HTTP_ENDPOINT = "http://192.168.10.220:8008/index.php?app=ws"


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_playsms_http_params(self, account, number, message):
        return {
            "h": account.sms_playsms_http_webtoken,
            "u": account.sms_playsms_http_login,
            "op": "pv",
            "from": account.sms_playsms_http_from,
            "to": number,
            "msg": message,
        }

    @api.model
    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    @api.model
    def _send_sms_with_playsms_http(self, number, message, sms_id):
        if not number:
            return "wrong_number_format"

        account = self._get_sms_account()
        response = requests.get(
            PLAYSMS_HTTP_ENDPOINT,
            params=self._prepare_playsms_http_params(account, number, message),
        ).text

        if not response:
            self.env["sms.sms"].browse(sms_id).error_detail = response
            return "server_error"

        return "success"

    @api.model
    def _is_sent_with_playsms(self):
        return self._get_sms_account().provider == "sms_playsms_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_playsms():
            raise NotImplementedError
        return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_playsms():
            if len(messages) != 1:
                raise UserError(_("Batch sending is not supported with PlaySMS"))

            return [
                {
                    "state": self._send_sms_with_playsms_http(
                        messages[0]["number"],
                        messages[0]["content"],
                        messages[0]["res_id"],
                    ),
                    "credit": 0,
                    "res_id": messages[0]["res_id"],
                }
            ]
        return super()._send_sms_batch(messages)
