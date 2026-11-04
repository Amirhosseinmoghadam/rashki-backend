"""Official TCart invoice contract; no remote API calls are made."""
import hashlib
import hmac
import json
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from payments.providers.tcart import TCartProvider
from payments.providers.base import PaymentProviderVerificationError

@override_settings(TCART_API_TOKEN='TEST_TOKEN', TCART_CALLBACK_SECRET='TEST_SECRET', TCART_RETURN_URL='https://example.org/return')
class TCartSecurityTests(SimpleTestCase):
    def setUp(self):
        self.provider=TCartProvider()
        self.attempt=SimpleNamespace(provider_reference='104', amount_toman=50000, provider_amount=50007, order=SimpleNamespace(order_number='ORD-1'))

    def test_valid_callback_signature(self):
        payload={'invoice_id':104,'event':'payment.confirmed'}
        blob=json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()
        sig=hmac.new(b'TEST_SECRET',blob,hashlib.sha256).hexdigest()
        self.assertTrue(TCartProvider.verify_callback_signature(payload,'sha256='+sig,'TEST_SECRET'))

    def test_callback_rejects_wrong_secret(self):
        payload={'invoice_id':104,'event':'payment.confirmed'}
        blob=json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()
        sig=hmac.new(b'WRONG',blob,hashlib.sha256).hexdigest()
        self.assertFalse(TCartProvider.verify_callback_signature(payload,'sha256='+sig,'TEST_SECRET'))

    def test_callback_rejects_malformed_signature(self):
        self.assertFalse(TCartProvider.verify_callback_signature({'invoice_id':104},'invalid','TEST_SECRET'))

    @patch.object(TCartProvider,'_call')
    def test_paid_invoice_requires_matching_unique_amount(self, call):
        call.return_value=dict(ok=True,invoice_id=104,status='paid',paid_at='2026-11-04T12:00:00',external_order_id='ORD-1',base_price_toman=50000,unique_amount_toman=50008)
        with self.assertRaises(PaymentProviderVerificationError):
            self.provider.verify_payment(attempt=self.attempt,callback_data={'status':'paid'})

    @patch.object(TCartProvider,'_call')
    def test_paid_invoice_requires_matching_order(self, call):
        call.return_value=dict(ok=True,invoice_id=104,status='paid',paid_at='2026-11-04T12:00:00',external_order_id='FOREIGN-ORDER',base_price_toman=50000,unique_amount_toman=50007)
        with self.assertRaises(PaymentProviderVerificationError):
            self.provider.verify_payment(attempt=self.attempt,callback_data={})

    @patch.object(TCartProvider,'_call')
    def test_paid_invoice_requires_paid_at(self, call):
        call.return_value=dict(ok=True,invoice_id=104,status='paid',external_order_id='ORD-1',base_price_toman=50000,unique_amount_toman=50007)
        with self.assertRaises(PaymentProviderVerificationError):
            self.provider.verify_payment(attempt=self.attempt,callback_data={})

    @patch.object(TCartProvider,'_call')
    def test_pending_invoice_cannot_be_spoofed_by_callback(self, call):
        call.return_value=dict(ok=True,invoice_id=104,status='pending')
        self.assertFalse(self.provider.verify_payment(attempt=self.attempt,callback_data={'status':'paid'}).success)

    @patch.object(TCartProvider,'_call')
    def test_paid_invoice_with_all_matching_fields(self, call):
        call.return_value=dict(ok=True,invoice_id=104,status='paid',paid_at='2026-11-04T12:00:00',external_order_id='ORD-1',base_price_toman=50000,unique_amount_toman=50007,tracking_code='TCO-TEST')
        result=self.provider.verify_payment(attempt=self.attempt,callback_data={'status':'pending'})
        self.assertTrue(result.success)
        self.assertEqual(result.provider_transaction_id,'TCO-TEST')
