============
Sms OVH HTTP
============

A modification of the original Implementation of **OVH http2sms API** for sending sms from OCA.
This module depend of odoo native **sms** module it only implement `PlaySMS <https://playsms.org>` as provider instead of odoo SA.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

* You need to set your playsms http end point i models/sms_api.py before installing module in odoo (will fix that whwn I get some help with python :-) )
* Go to IAP menu
* Create a new account with **SMS OVH HTTP** as provider
* Fill your account information
* You can now send an sms

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/waltherB/sms-playsms-http/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://https://github.com/waltherB/sms-playsms-http/issues/new?body=module:%20sms_playsms_http%0Aversion:%2014.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits to the original contributors at OCA
=======

Authors
~~~~~~~

* Akretion

Contributors
~~~~~~~~~~~~

* Sébastien BEAU 


You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
