from datetime import timedelta
from django.utils import timezone

from discounts.api.v1.serializers import DiscountCodeSerializer, DiscountValidateSerializer
from .base import DiscountBase


class DiscountSerializerTests(DiscountBase):
    def test_normalizes_code(self):
        s = DiscountCodeSerializer(data=self.admin_payload(" off۱۲ "))
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["code"], "OFF12")

    def test_rejects_invalid_code_characters(self):
        s = DiscountCodeSerializer(data=self.admin_payload("BAD CODE!"))
        self.assertFalse(s.is_valid())
        self.assertIn("code", s.errors)

    def test_duplicate_code(self):
        s = DiscountCodeSerializer(data=self.admin_payload("off20"))
        self.assertFalse(s.is_valid())
        self.assertIn("code", s.errors)

    def test_percentage_required(self):
        s = DiscountCodeSerializer(data={"code": "ONE", "discount_type": "percentage"})
        self.assertFalse(s.is_valid())
        self.assertIn("percentage", s.errors)

    def test_fixed_amount_required(self):
        s = DiscountCodeSerializer(data={"code": "ONE", "discount_type": "fixed_amount"})
        self.assertFalse(s.is_valid())
        self.assertIn("fixed_amount_toman", s.errors)

    def test_end_date_must_follow_start(self):
        now = timezone.now()
        s = DiscountCodeSerializer(data=self.admin_payload("DATE", start_at=now.isoformat(),
                                               end_at=(now - timedelta(days=1)).isoformat()))
        self.assertFalse(s.is_valid())
        self.assertIn("end_at", s.errors)

    def test_products_scope_requires_selection(self):
        s = DiscountCodeSerializer(data=self.admin_payload("ITEM", scope="products"))
        self.assertFalse(s.is_valid())
        self.assertIn("product_ids", s.errors)

    def test_categories_scope_requires_selection(self):
        s = DiscountCodeSerializer(data=self.admin_payload("CAT", scope="categories"))
        self.assertFalse(s.is_valid())
        self.assertIn("category_ids", s.errors)

    def test_partial_update_keeps_other_fields(self):
        s = DiscountCodeSerializer(self.discount, data={"description": "Updated"}, partial=True)
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.description, "Updated")

    def test_validate_cart_rejects_empty(self):
        s = DiscountValidateSerializer(data={"code": "OFF20", "items": []})
        self.assertFalse(s.is_valid())
        self.assertIn("items", s.errors)

    def test_validate_cart_rejects_duplicate_product(self):
        s = DiscountValidateSerializer(data={"code": "OFF20", "items": [
            {"product_id": 1, "quantity": 1}, {"product_id": 1, "quantity": 2}]})
        self.assertFalse(s.is_valid())
        self.assertIn("items", s.errors)

    def test_validate_cart_rejects_zero_quantity(self):
        s = DiscountValidateSerializer(data={"code": "OFF20", "items": [{"product_id": 1, "quantity": 0}]})
        self.assertFalse(s.is_valid())
        self.assertIn("items", s.errors)

    def test_validate_cart_normalizes_code(self):
        s = DiscountValidateSerializer(data={"code": " off۲۰ ", "items": [{"product_id": 1, "quantity": 1}]})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["code"], "OFF20")
