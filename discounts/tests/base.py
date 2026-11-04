from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from discounts.models import DiscountCode
from discounts.services import DiscountLine


class DiscountBase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(phone_number="09120000101")
        self.other_user = get_user_model().objects.create_user(phone_number="09120000102")
        self.admin = get_user_model().objects.create_user(phone_number="09120000103")
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])
        self.client = APIClient()
        self.discount = self.make_discount()

    def make_discount(self, **overrides):
        data = dict(
            code="OFF20", discount_type=DiscountCode.DiscountType.PERCENTAGE,
            percentage=Decimal("20.00"), scope=DiscountCode.Scope.ALL,
            start_at=timezone.now() - timedelta(days=1),
            end_at=timezone.now() + timedelta(days=1),
            is_active=True,
        )
        data.update(overrides)
        return DiscountCode.objects.create(**data)

    @staticmethod
    def lines(*prices):
        # ALL scope needs only pk and category_id; no Product database records.
        return [DiscountLine(SimpleNamespace(pk=i + 1, category_id=None), 1, p)
                for i, p in enumerate(prices)]

    @staticmethod
    def admin_payload(code="NEWCODE", **overrides):
        data = {"code": code, "discount_type": "percentage", "percentage": "15.00", "scope": "all"}
        data.update(overrides)
        return data
