"""Mocked contract tests; run using Django's test runner, no actual TCart requests."""
import hashlib
import hmac
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from payments.providers.base import PaymentProviderVerificationError
from payments.providers.tcart import TCartProvider


@override_settings(TCART_API_TOKEN="unit-test-key", TCART_CALLBACK_SECRET="unit-test-secret",
                   TCART_RETURN_URL="https://example.org/payment/return")
class TCartProviderTests(SimpleTestCase):
    def setUp(self):
        self.provider = TCartProvider()
        self.attempt = SimpleNamespace(
            provider_reference="104", amount_toman=50000, provider_amount=50007,
            order=SimpleNamespace(order_number="ORDER-1")
        )

    def test_signature_valid(self):
        data = {"status": "paid", "invoice_id": 104}
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
        sig = hmac.new(b"unit-test-secret", raw.encode(), hashlib.sha256).hexdigest()
        self.assertTrue(TCartProvider.verify_callback_signature(data, "sha256=" + sig, "unit-test-secret"))
        self.assertFalse(TCartProvider.verify_callback_signature(data, "sha256=" + sig, "different-secret"))

    @patch.object(TCartProvider, "_call")
    def test_paid_invoice_requires_matching_amounts(self, call):
        call.return_value = {
            "ok": True, "invoice_id": 104, "status": "paid", "paid_at": "2026-11-04T12:00:00",
            "external_order_id": "ORDER-1", "base_price_toman": 50000,
            "unique_amount_toman": 50007, "tracking_code": "TCO-TEST"
        }
        result = self.provider.verify_payment(attempt=self.attempt, callback_data={"status": "fake"})
        self.assertTrue(result.success)
        self.assertEqual(result.provider_transaction_id, "TCO-TEST")
        call.return_value["unique_amount_toman"] = 50008
        with self.assertRaises(PaymentProviderVerificationError):
            self.provider.verify_payment(attempt=self.attempt, callback_data={})

    @patch.object(TCartProvider, "_call")
    def test_pending_invoice_never_marks_paid(self, call):
        call.return_value = {"ok": True, "invoice_id": 104, "status": "pending"}
        result = self.provider.verify_payment(attempt=self.attempt, callback_data={"status": "paid"})
        self.assertFalse(result.success)
        self.assertEqual(result.failure_code, "pending")
