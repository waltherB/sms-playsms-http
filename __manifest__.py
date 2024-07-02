{
    "name": "Sms PlaySMS HTTP",
    "summary": "Send sms using PlaySMS http API",
    "version": "17.0.1.0",
    "category": "SMS",
    "website": "https://github.com/waltherB/sms-playsms-http",
    "author": "Walther Barnett",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["base_phone", "sms", "iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_sms_view.xml",
    ],
    "demo": [],
    "qweb": [],
}
