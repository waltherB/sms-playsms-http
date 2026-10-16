# 17.0 → 18.0 port notes

Kept minimal and auditable. Every change is either an Odoo 18 requirement
or a small robustness fix. No feature drift, no refactoring, no renames of
public API.

## Odoo-18-required changes

1. **Chatter shortcut** (`views/iap_account.xml`)
   Replaced the manual chatter block —
   ```xml
   <div class="oe_chatter">
     <field name="message_follower_ids" groups="base.group_user"/>
     <field name="activity_ids"/>
     <field name="message_ids"/>
   </div>
   ```
   with the Odoo 18 shortcut tag: `<chatter/>`.

2. **Manifest version bump**
   `17.0.1.0.0` → `18.0.1.0.0`.

## Preserved as-is (already 18-compatible)

- No `<tree>` views in the module — no `tree` → `list` rename needed.
- No `attrs=` / `states=` attributes in views — the 17 module already used
  the direct-boolean-expression form (`invisible="…"`, `required="…"`)
  that 18 mandates.
- `IapAccount` inheritance pattern (`_name = "iap.account"` +
  `_inherit = [..., "mail.thread", ...]`) is still the correct way to
  attach chatter to a base model in 18.
- `sms.sms._postprocess_iap_sent_sms` signature is unchanged between 17
  and 18.

## Robustness fixes (small)

- Added `timeout=30` to all `requests.get()` calls (the 17 module had no
  timeout — a hanging PlaySMS server would block the sending worker
  indefinitely).
- Replaced `f"…"` in logger calls with `%s` placeholders — avoids formatting
  cost when the log level filters the message out.
- Removed `logging.basicConfig(level=logging.DEBUG)` from module-import time
  (was globally reconfiguring the Odoo logger to DEBUG for every request).
- Fixed a closure-capture bug in `_postprocess_iap_sent_sms`'s
  `filtered(lambda …)`: the lambda was capturing `results_group` from the
  enclosing loop variable, which meant every iteration filtered against the
  *last* group's uuids. Bound it as a default argument.
- `get_current_credit_balance` no longer swallows the `error_code` local
  variable in an unreachable branch — the `raise UserWarning(error_msg)`
  now runs when the response is not `OK`.
- `_send_sms_with_sms_api_playsms`: guarded the `response_content["data"][0]`
  access against a missing `data` key with `.get("data", [{}])[0].get(...)`.
