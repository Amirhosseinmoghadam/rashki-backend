from rest_framework.test import APIRequestFactory, force_authenticate
from discounts.api.v1.views import DiscountCodeViewSet, DiscountValidateAPIView
from .base import DiscountBase


class DiscountPermissionTests(DiscountBase):
    def list_request(self, user=None):
        req = APIRequestFactory().get("/discount-codes/")
        if user is not None:
            force_authenticate(req, user=user)
        return DiscountCodeViewSet.as_view({"get": "list"})(req)

    def test_anonymous_cannot_list_codes(self):
        self.assertIn(self.list_request().status_code, (401, 403))

    def test_regular_user_cannot_list_codes(self):
        self.assertEqual(self.list_request(self.user).status_code, 403)

    def test_admin_can_list_codes(self):
        self.assertEqual(self.list_request(self.admin).status_code, 200)

    def test_anonymous_cannot_validate_code(self):
        req = APIRequestFactory().post("/discounts/validate/", {}, format="json")
        response = DiscountValidateAPIView.as_view()(req)
        self.assertIn(response.status_code, (401, 403))

    def test_regular_user_can_reach_validate_serializer(self):
        req = APIRequestFactory().post("/discounts/validate/", {}, format="json")
        force_authenticate(req, user=self.user)
        response = DiscountValidateAPIView.as_view()(req)
        self.assertEqual(response.status_code, 400)
