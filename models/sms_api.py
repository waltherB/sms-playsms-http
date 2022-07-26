# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


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
            "op":"pv",
            #"password": account.sms_playsms_http_password,
            "from": account.sms_playsms_http_from,
            "to": number,
            "msg": message,
            #"noStop": 1,
        }

    def _get_sms_account(self):
        return self.env["iap.account"].get("sms")

    def _send_sms_with_playsms_http(self, number, message, sms_id):
        # Try to return same error code like odoo
        # list is here: self.IAP_TO_SMS_STATE
        if not number:
            return "wrong_number_format"
        account = self._get_sms_account()
        r = requests.get(
            PLAYSMS_HTTP_ENDPOINT,
            params=self._prepare_playsms_http_params(account, number, message),
        )
        response = r.text
        #if response[0:2] != "OK":
        if not r:
            self.env["sms.sms"].browse(sms_id).error_detail = response
            return "server_error"
        else:
            return "success"

    def _is_sent_with_playsms(self):
        return self._get_sms_account().provider == "sms_playsms_http"

    @api.model
    def _send_sms(self, numbers, message):
        if self._is_sent_with_playsms():
            # This method seem to be deprecated (no odoo code use it)
            # as OVH do not support it we do not support it
            # Note: if you want to implement it becarefull just looping
            # on the list of number is not the right way to do it.
            # If you have an error, you will send and send again the same
            # message
            raise NotImplementedError
        else:
            return super()._send_sms(numbers, message)

    @api.model
    def _send_sms_batch(self, messages):
        if self._is_sent_with_playsms():
            if len(messages) != 1:
                # we already have inherited the split_batch method on sms.sms
                # so this case shouldsnot append
                raise UserError(_("Batch sending is not support with PlaySMS"))
            state = self._send_sms_with_playsms_http(
                messages[0]["number"], messages[0]["content"], messages[0]["res_id"]
            )
            return [{"state": state, "credit": 0, "res_id": messages[0]["res_id"]}]
        else:
            return super()._send_sms_batch(messages)
