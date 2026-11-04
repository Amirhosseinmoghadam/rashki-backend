from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIRequestFactory, force_authenticate

from discounts.api.v1.views import DiscountCodeViewSet, DiscountValidateAPIView
from discounts.models import DiscountCode
from .base import DiscountBase


class DiscountViewTests(DiscountBase):
    def dispatch(self, action, method="get", payload=None, user=None, pk=None):
        factory = APIRequestFactory()
        request = getattr(factory, method)("/api/v1/discount-codes/", payload or {}, format="json")
        if user is not None:
            force_authenticate(request, user=user)
        mapping = {method: action}
        view = DiscountCodeViewSet.as_view(mapping)
        return view(request, **({"pk": pk} if pk is not None else {}))

    def test_admin_list(self):
        response = self.dispatch("list", user=self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["count"], 1)

    def test_admin_detail(self):
        response = self.dispatch("retrieve", user=self.admin, pk=self.discount.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["code"], "OFF20")

    def test_admin_create(self):
        response = self.dispatch("create", "post", self.admin_payload(), self.admin)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(DiscountCode.objects.filter(code="NEWCODE").exists())

    def test_admin_patch(self):
        response = self.dispatch("partial_update", "patch", {"description": "Changed"},
                                 self.admin, self.discount.pk)
        self.assertEqual(response.status_code, 200, response.data)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.description, "Changed")

    def test_admin_delete(self):
        response = self.dispatch("destroy", "delete", user=self.admin, pk=self.discount.pk)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DiscountCode.objects.filter(pk=self.discount.pk).exists())

    def test_validate_missing_code_returns_400(self):
        factory = APIRequestFactory()
        request = factory.post("/discounts/validate/", {
            "code": "UNKNOWN", "items": [{"product_id": 1, "quantity": 1}]}, format="json")
        force_authenticate(request, user=self.user)
        response = DiscountValidateAPIView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
