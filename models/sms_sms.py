from odoo import fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_playsms():
            # No batch with PLAYSMS
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
