# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

import logging
import requests

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class IapAccount(models.Model):
    _name = "iap.account"
    _inherit = ['iap.account', 'mail.thread', 'mail.activity.mixin']

    provider = fields.Selection(
        selection_add=[("sms_api_playsms", "PlaySMS")],
        ondelete={"sms_api_playsms": "cascade"},
    )
    sms_api_url = fields.Char(help="PlaySMS url eg.: https://playsms.example.com/index.php?app=ws")
    sms_api_username = fields.Char(help="PlaySMS username")
    sms_api_password = fields.Char(help="PlaySMS webtoken")
    sms_api_from = fields.Char(help="Sender number, Sender ID or description")
    sms_api_min_tokens = fields.Integer(string="Minimum credits", help="Minimum credit level for alerting purposes. If it is a negative number, e.g. -1, the alarming is disabled.")
    @api.model
    def _default_sms_api_token_notification_action(self):
        try:
            default_action = self.env.ref('playsms_connector.model_iap_account_action_low_tokens').id
        except ValueError:
            _logger.warning("playsms_connector.model_iap_account_action_low_tokens doesn't exist - notification action will have no default.")
            return None
        else:
            return default_action

    sms_api_token_notification_action = fields.Many2one('ir.actions.server', default=_default_sms_api_token_notification_action, string="Credits notification action", help="Action to be performed when the number of credits is less than min_tokens.")
    sms_api_playsms_connection_status = fields.Char(string="Connection status", help="Status of the last connection test.")
    @api.model
    def check_sms_api_playsms_credit_balance(self):
        """If current credits are lower than sms_api_min_tokens, execute sms_api_token_notification_action"""

        iap_account = self._get_sms_account()

        if iap_account.sms_api_min_tokens < 0:
            _logger.info(f"PlaySMS minimum credits not set. Skipping balance check.")
            return

        if not iap_account.sms_api_token_notification_action:
            _logger.info(f"PlaySMS notification action not set. Skipping balance check.")
            return

        try:
            api_credits = iap_account.get_current_credit_balance()
        except UserWarning as e:
            _logger.warning(f"PlaySMS returned an error while attempting to get current credit balance: {e}")
        except Exception as e:
            _logger.warning(f"An exception occurred while attempting to get current credit balance: {e}")
        else:
            if int(api_credits) < int(iap_account.sms_api_min_tokens):
                _logger.info(f"You only have {api_credits} PlaySMS credits left.")
                ctx = dict(self.env.context or {})
                ctx.update({'active_id': iap_account.id, 'active_model': 'iap.account'})
                iap_account.sms_api_token_notification_action.with_context(ctx).run()
            else:
                _logger.info(f"You have {api_credits} PlaySMS credits, which is more than your set minimum of {iap_account.sms_api_min_tokens} credits")

    def _prepare_sms_api_playsms_credit_check_params(self):
        self.ensure_one()

        params = {
            "op":"cr", 
            "u": self.sms_api_username,
            "h": self.sms_api_password,
        }

        return params
    def get_current_credit_balance(self):

        iap_account_sms = self.env['iap.account']._get_sms_account()

        response = requests.get(
            iap_account_sms.sms_api_url,
            params=self._prepare_sms_api_playsms_credit_check_params(),
        )

        response_content = response.json()  # Parse the JSON response
        _logger.debug(f"PlaySMS credit balance check responded with: {response_content}")

        if response_content['status'] == "OK":
           current_credit_balance = response_content['credit']
           return current_credit_balance
        else:
           error_code = response_content['error']
           error_msg = response_content['error_string']
        raise UserWarning(error_msg)

    @api.model
    def _get_sms_account(self):
        return self.get("sms")

    def sms_api_playsms_connection_test(self):
        """Test connection by checking current credit balance and writing a status message to sms_api_playsms_connection_status
        """

        iap_account = self._get_sms_account()
        if iap_account.id != self.id or self.provider != "sms_api_playsms":
            _logger.warning("PlaySMS connection test is only performed on SMS account where PlaySMS is set as provider.")

        try:
            api_credits = iap_account.get_current_credit_balance()
        except UserWarning as e:
            _logger.warning(f"PlaySMS returned an error while attempting to get current credit balance: {e}")
            iap_account.sms_api_playsms_connection_status = e
        except Exception as e:
            _logger.warning(f"An exception occurred while attempting to get current credit balance: {e}")
            iap_account.sms_api_playsms_connection_status = _("Unexpected error. Check server log for more info.")
        else:
            _logger.info("PlaySMS connection test successful")
            iap_account.sms_api_playsms_connection_status = "OK"
