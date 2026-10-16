# -*- coding: utf-8 -*-
# Copyright 2024 Walther Barnett (original 17.0 author)
# Copyright 2026 Entuura (Asia) Limited — 18.0 port
# @author Steven Uggowitzer <steven@entuura.org>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "PlaySMS Connector",
    "summary": "Send SMS via a self-hosted PlaySMS gateway (Odoo 18 port)",
    "author": (
        "Walther Barnett, "
        "Entuura (Asia) Limited"
    ),
    "website": "https://gitea.entuura.com/EntCommercial/playsms-connector",
    "license": "AGPL-3",
    "category": "Technical",
    "version": "18.0.1.0.0",
    "depends": [
        "base",
        "sms",
        "iap_alternative_provider",
        "phone_validation",
    ],
    "external_dependencies": {
        "python": ["phonenumbers", "requests"],
    },
    "data": [
        "data/iap_account_data.xml",
        "data/ir_cron.xml",
        "views/iap_account.xml",
        "views/sms_sms.xml",
        "views/sms_resend.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
}
