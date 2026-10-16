# -*- coding: utf-8 -*-
# Copyright 2024 Walther Barnett (original 17.0 author)
# Copyright 2026 Entuura (Asia) Limited — 18.0 port
# @author Steven Uggowitzer <steven@entuura.org>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class Sms(models.Model):
    _inherit = "sms.sms"

    sms_api_error = fields.Char()

    def _prepare_sms_api_playsms_params(self, iap_account):
        self.ensure_one()
        return {
            "op": "pv",
            "u": iap_account.sms_api_username,
            "h": iap_account.sms_api_password,
            "from": iap_account.sms_api_from,
            "to": self.number,
            "msg": self.body,
        }

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """Try to send SMS after checking the number (presence and formatting)."""
        if self._is_sent_with_sms_api():
            try:
                result = self._send_sms_with_sms_api_playsms()
                iap_results = [{"uuid": sms.uuid, "state": result} for sms in self]
            except Exception as e:
                _logger.warning(
                    "Sent batch %s SMS: %s: failed with exception %s",
                    len(self.ids),
                    self.ids,
                    e,
                )
                if raise_exception:
                    raise
                self._postprocess_iap_sent_sms(
                    [{"res_id": sms.id, "state": "server_error"} for sms in self],
                    unlink_failed=unlink_failed,
                    unlink_sent=unlink_sent,
                )
            else:
                _logger.info(
                    "Send batch %s SMS: %s: gave %s",
                    len(self.ids),
                    self.ids,
                    iap_results,
                )
                self._postprocess_iap_sent_sms(
                    iap_results,
                    unlink_failed=unlink_failed,
                    unlink_sent=unlink_sent,
                )
        else:
            return super()._send(
                unlink_failed=unlink_failed,
                unlink_sent=unlink_sent,
                raise_exception=raise_exception,
            )

    def _is_sent_with_sms_api(self):
        return (
            self.env["iap.account"]._get_sms_account().provider == "sms_api_playsms"
        )

    def _send_sms_with_sms_api_playsms(self):
        self.ensure_one()
        if not self.number:
            return "wrong_number_format"

        iap_account_sms = self.env["iap.account"]._get_sms_account()

        response = requests.get(
            iap_account_sms.sms_api_url,
            params=self._prepare_sms_api_playsms_params(iap_account_sms),
            timeout=30,
        )

        response_content = response.json()
        _logger.debug("PlaySMS responded with: %s", response_content)

        if response_content.get("data", [{}])[0].get("status") == "OK":
            _logger.info("SMS sent successfully")
            self.sms_api_error = False
            return "success"

        error_code = response_content.get("error")
        error_msg = response_content.get("error_string")
        _logger.warning(
            "Failed to send SMS: %s : %s", error_code, error_msg
        )
        self.sms_api_error = error_msg
        return error_msg

    def _split_batch(self):
        if self._is_sent_with_sms_api():
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()

    def _postprocess_iap_sent_sms(
        self, results, unlink_failed=False, unlink_sent=True
    ):
        results_uuids = [result["uuid"] for result in results]
        all_sms_sudo = (
            self.env["sms.sms"]
            .sudo()
            .search([("uuid", "in", results_uuids)])
            .with_context(sms_skip_msg_notification=True)
        )

        for iap_state, results_group in tools.groupby(
            results, key=lambda result: result["state"]
        ):
            sms_sudo = all_sms_sudo.filtered(
                lambda s, results_group=results_group: s.uuid
                in {result["uuid"] for result in results_group}
            )
            if success_state := self.IAP_TO_SMS_STATE_SUCCESS.get(iap_state):
                sms_sudo.sms_tracker_id._action_update_from_sms_state(success_state)
                to_delete = {"to_delete": True} if unlink_sent else {}
                sms_sudo.write(
                    {"state": success_state, "failure_type": False, **to_delete}
                )
            else:
                failure_type = self.IAP_TO_SMS_FAILURE_TYPE.get(iap_state, "unknown")
                if failure_type != "unknown":
                    sms_sudo.sms_tracker_id._action_update_from_sms_state(
                        "error", failure_type=failure_type
                    )
                else:
                    sms_sudo.sms_tracker_id._action_update_from_provider_error(
                        iap_state
                    )
                to_delete = {"to_delete": True} if unlink_failed else {}
                sms_sudo.write(
                    {"state": "error", "failure_type": failure_type, **to_delete}
                )

        all_sms_sudo.mail_message_id._notify_message_notification_update()
