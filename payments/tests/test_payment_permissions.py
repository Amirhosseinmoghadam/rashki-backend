from django.test import SimpleTestCase
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from payments.api.v1.views import (PaymentStartAPIView, PaymentDetailAPIView, ZarinPalCallbackAPIView, TCartCallbackAPIView, PaymentRefundCreateAPIView, PaymentRefundDetailAPIView, PaymentRefundExecuteAPIView)

class PaymentPermissionContractTests(SimpleTestCase):
    def test_start_requires_authentication(self):
        self.assertIn(IsAuthenticated, PaymentStartAPIView.permission_classes)

    def test_detail_requires_authentication(self):
        self.assertIn(IsAuthenticated, PaymentDetailAPIView.permission_classes)

    def test_zarinpal_callback_allows_anonymous(self):
        self.assertIn(AllowAny, ZarinPalCallbackAPIView.permission_classes)

    def test_tcart_callback_allows_anonymous_transport(self):
        # Anonymous transport does NOT mean unsigned callbacks are trusted.
        self.assertIn(AllowAny, TCartCallbackAPIView.permission_classes)

    def test_refund_creation_requires_staff(self):
        self.assertIn(IsAdminUser, PaymentRefundCreateAPIView.permission_classes)

    def test_refund_execution_requires_staff(self):
        self.assertIn(IsAdminUser, PaymentRefundExecuteAPIView.permission_classes)

    def test_refund_detail_requires_staff(self):
        self.assertIn(IsAdminUser, PaymentRefundDetailAPIView.permission_classes)
