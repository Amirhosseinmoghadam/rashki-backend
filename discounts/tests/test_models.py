from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from discounts.models import DiscountCode, DiscountUsage
from .base import DiscountBase


class DiscountModelTests(DiscountBase):
    def test_normalizes_code_on_save(self):
        d = self.make_discount(code=" off۱۲ ")
        self.assertEqual(d.code, "OFF12")

    def test_string_representation(self):
        self.assertEqual(str(self.discount), "OFF20")

    def test_code_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_discount(code="OFF20")

    def test_percentage_requires_percentage(self):
        d = self.discount
        d.percentage = None
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_fixed_requires_amount(self):
        d = self.discount
        d.discount_type = DiscountCode.DiscountType.FIXED_AMOUNT
        d.fixed_amount_toman = None
        with self.assertRaises(ValidationError):
            d.full_clean()

    def test_percentage_above_hundred_rejected(self):
        self.discount.percentage = Decimal("101")
        with self.assertRaises(ValidationError):
            self.discount.full_clean()

    def test_end_before_start_rejected(self):
        self.discount.end_at = self.discount.start_at - timedelta(seconds=1)
        with self.assertRaises(ValidationError):
            self.discount.full_clean()

    def test_fixed_save_clears_percentage_and_cap(self):
        d = self.make_discount(code="FIX10", discount_type="fixed_amount", fixed_amount_toman=1000,
                               percentage=Decimal("10"), maximum_discount_toman=10000)
        self.assertIsNone(d.percentage)
        self.assertIsNone(d.maximum_discount_toman)

    def test_percentage_save_clears_fixed_amount(self):
        d = self.make_discount(code="PER10", fixed_amount_toman=1000)
        self.assertIsNone(d.fixed_amount_toman)

    def test_usage_reference_is_unique(self):
        self.make_usage(reference="ORDER-1")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_usage(reference="ORDER-1")

    def make_usage(self, **kwargs):
        data = dict(discount=self.discount, user=self.user, reference="ORDER-1",
                    code_snapshot=self.discount.code, subtotal_toman=10000,
                    eligible_subtotal_toman=10000, discount_amount_toman=2000)
        data.update(kwargs)
        return DiscountUsage.objects.create(**data)
