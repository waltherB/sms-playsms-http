import requests

from odoo import _, api, models
from odoo.exceptions import UserError

class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_playsms_http_params(self, account, number, message):
        return {
            "u": account.sms_playsms_http_login,
            "h": account.sms_playsms_http_webtoken,
            "op": "pv",
            "to": number,
            "msg": message,
        }

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _send_sms_with_playsms_http(self, number, message, sms_id):
        if not number:
            return "wrong_number_format"
        account = self._get_sms_account()
        r = requests.get(
            account.sms_playsms_http_endpoint,
            params=self._prepare_playsms_http_params(account, number, message),
        )
        response = r.json()
        if response['status'] != 'OK':
            self.env["sms.sms"].browse(sms_id).error_detail = response['error_string']
            return "server_error"
        return "success"

    def _is_sent_with_playsms(self):
        return self._get_sms_account().provider == "sms_playsms_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_playsms():
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_playsms():
            if len(messages) != 1:
                raise UserError(_("Batch sending is not support with PlaySMS"))
            state = self._send_sms_with_playsms_http(
                messages[0]["number"], messages[0]["content"], messages[0]["res_id"]
            )
            return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)

