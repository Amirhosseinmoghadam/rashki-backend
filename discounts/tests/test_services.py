from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

from discounts.models import DiscountUsage
from discounts.services import (
    DiscountValidationError, calculate_discount, consume_discount,
    get_discount_by_code, normalize_discount_code, revoke_discount_usage,
    validate_usage_limits,
)
from .base import DiscountBase


class DiscountServiceTests(DiscountBase):
    def calc(self, *prices, discount=None, user=None):
        return calculate_discount(discount=discount or self.discount,
                                  lines=self.lines(*prices), user=user or self.user)

    def test_normalize_code(self):
        self.assertEqual(normalize_discount_code(" off۱۲ "), "OFF12")

    def test_get_discount_case_insensitive_normalized(self):
        self.assertEqual(get_discount_by_code(" off20 ").pk, self.discount.pk)

    def test_unknown_code(self):
        with self.assertRaises(DiscountValidationError):
            get_discount_by_code("NOT_FOUND")

    def test_percentage_amount_and_totals(self):
        result = self.calc(10000, 5000)
        self.assertEqual((result.subtotal_toman, result.eligible_subtotal_toman,
                          result.discount_amount_toman, result.final_subtotal_toman),
                         (15000, 15000, 3000, 12000))

    def test_round_half_up(self):
        self.discount.percentage = Decimal("12.50")
        self.assertEqual(self.calc(4).discount_amount_toman, 1)

    def test_percentage_cap(self):
        self.discount.maximum_discount_toman = 1000
        self.assertEqual(self.calc(10000).discount_amount_toman, 1000)

    def test_fixed_amount(self):
        d = self.make_discount(code="FIXED", discount_type="fixed_amount", fixed_amount_toman=3000)
        self.assertEqual(self.calc(10000, discount=d).discount_amount_toman, 3000)

    def test_fixed_cannot_exceed_eligible_subtotal(self):
        d = self.make_discount(code="FIXED", discount_type="fixed_amount", fixed_amount_toman=50000)
        result = self.calc(10000, discount=d)
        self.assertEqual((result.discount_amount_toman, result.final_subtotal_toman), (10000, 0))

    def test_inactive_code(self):
        self.discount.is_active = False
        with self.assertRaises(DiscountValidationError):
            self.calc(10000)

    def test_not_started(self):
        self.discount.start_at = timezone.now() + timedelta(days=1)
        with self.assertRaises(DiscountValidationError):
            self.calc(10000)

    def test_expired(self):
        self.discount.end_at = timezone.now() - timedelta(seconds=1)
        with self.assertRaises(DiscountValidationError):
            self.calc(10000)

    def test_empty_cart(self):
        with self.assertRaises(DiscountValidationError):
            self.calc()

    def test_minimum_order(self):
        self.discount.minimum_order_toman = 10001
        with self.assertRaises(DiscountValidationError):
            self.calc(10000)

    def test_global_usage_limit_blocks_second_order(self):
        self.discount.usage_limit = 1
        self.discount.save(update_fields=["usage_limit"])
        consume_discount(discount=self.discount, user=self.user,
                         lines=self.lines(10000), reference="ORDER-1")
        with self.assertRaises(DiscountValidationError):
            consume_discount(discount=self.discount, user=self.other_user,
                             lines=self.lines(10000), reference="ORDER-2")
        self.assertEqual(DiscountUsage.objects.count(), 1)

    def test_per_user_limit_blocks_repeat(self):
        self.discount.usage_limit_per_user = 1
        self.discount.save(update_fields=["usage_limit_per_user"])
        consume_discount(discount=self.discount, user=self.user,
                         lines=self.lines(10000), reference="ORDER-1")
        with self.assertRaises(DiscountValidationError):
            validate_usage_limits(self.discount, self.user)
        validate_usage_limits(self.discount, self.other_user)
        with self.assertRaises(DiscountValidationError):
            consume_discount(discount=self.discount, user=self.user,
                             lines=self.lines(10000), reference="ORDER-2")
        self.assertEqual(DiscountUsage.objects.count(), 1)

    def test_per_user_limit_requires_login(self):
        self.discount.usage_limit_per_user = 1
        with self.assertRaises(DiscountValidationError):
            calculate_discount(discount=self.discount, lines=self.lines(10000), user=None)

    def test_consumption_creates_snapshot(self):
        usage = consume_discount(discount=self.discount, user=self.user,
                                 lines=self.lines(10000), reference="ORDER-1")
        self.assertEqual((usage.code_snapshot, usage.subtotal_toman,
                          usage.discount_amount_toman, usage.status),
                         ("OFF20", 10000, 2000, DiscountUsage.Status.USED))

    def test_same_reference_is_idempotent(self):
        first = consume_discount(discount=self.discount, user=self.user,
                                 lines=self.lines(10000), reference="ORDER-1")
        second = consume_discount(discount=self.discount, user=self.user,
                                  lines=self.lines(10000), reference="ORDER-1")
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(DiscountUsage.objects.count(), 1)

    def test_same_reference_other_code_rejected(self):
        consume_discount(discount=self.discount, user=self.user,
                         lines=self.lines(10000), reference="ORDER-1")
        other = self.make_discount(code="OTHER")
        with self.assertRaises(DiscountValidationError):
            consume_discount(discount=other, user=self.user,
                             lines=self.lines(10000), reference="ORDER-1")

    def test_blank_reference_rejected(self):
        with self.assertRaises(DiscountValidationError):
            consume_discount(discount=self.discount, user=self.user,
                             lines=self.lines(10000), reference="  ")

    def test_revoke_is_idempotent_and_restores_capacity(self):
        self.discount.usage_limit = 1
        self.discount.save(update_fields=["usage_limit"])
        consume_discount(discount=self.discount, user=self.user,
                         lines=self.lines(10000), reference="ORDER-1")
        first = revoke_discount_usage("ORDER-1")
        self.assertEqual(first.status, DiscountUsage.Status.REVOKED)
        self.assertIsNotNone(first.revoked_at)
        self.assertEqual(revoke_discount_usage("ORDER-1").pk, first.pk)
        validate_usage_limits(self.discount, self.user)

    def test_revoke_unknown_reference(self):
        with self.assertRaises(DiscountValidationError):
            revoke_discount_usage("MISSING")
