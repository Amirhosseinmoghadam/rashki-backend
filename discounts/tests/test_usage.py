from django.db.models.deletion import ProtectedError
from django.db import transaction

from discounts.models import DiscountUsage
from discounts.services import consume_discount
from .base import DiscountBase


class DiscountUsageTests(DiscountBase):
    def test_usage_protects_discount_from_deletion(self):
        consume_discount(discount=self.discount, user=self.user,
                         lines=self.lines(10000), reference="ORDER-1")
        with self.assertRaises(ProtectedError):
            self.discount.delete()

    def test_usage_preserves_code_snapshot_after_rename(self):
        usage = consume_discount(discount=self.discount, user=self.user,
                                 lines=self.lines(10000), reference="ORDER-1")
        self.discount.code = "NEWNAME"
        self.discount.save()
        usage.refresh_from_db()
        self.assertEqual(usage.code_snapshot, "OFF20")

    def test_usage_status_defaults_used(self):
        usage = DiscountUsage.objects.create(
            discount=self.discount, user=self.user, reference="ORDER-1",
            code_snapshot="OFF20", subtotal_toman=10000,
            eligible_subtotal_toman=10000, discount_amount_toman=2000)
        self.assertEqual(usage.status, DiscountUsage.Status.USED)
