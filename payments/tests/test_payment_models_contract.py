"""Schema and invariants, without touching the production database."""
from django.test import SimpleTestCase
from django.db.models import PROTECT
from payments.models import PaymentAttempt, PaymentRefund

class PaymentSchemaTests(SimpleTestCase):
    def test_supported_providers(self):
        self.assertIn('zarinpal', PaymentAttempt.Provider.values)
        self.assertIn('tcart', PaymentAttempt.Provider.values)

    def test_attempt_public_identifier_is_unique(self):
        self.assertTrue(PaymentAttempt._meta.get_field('public_id').unique)

    def test_attempt_idempotency_key_is_unique(self):
        self.assertTrue(PaymentAttempt._meta.get_field('idempotency_key').unique)

    def test_attempt_protects_order_deletion(self):
        self.assertIs(PaymentAttempt._meta.get_field('order').remote_field.on_delete, PROTECT)

    def test_payment_has_unique_success_constraint(self):
        self.assertIn('unique_successful_payment_per_order', [c.name for c in PaymentAttempt._meta.constraints])

    def test_attempt_has_amount_snapshot(self):
        for key in ('amount_toman', 'provider_amount', 'provider_currency', 'provider_adjustment_toman'):
            with self.subTest(key=key):
                self.assertIsNotNone(PaymentAttempt._meta.get_field(key))

    def test_refund_links_protected(self):
        for key in ('order', 'payment_attempt'):
            with self.subTest(key=key):
                self.assertIs(PaymentRefund._meta.get_field(key).remote_field.on_delete, PROTECT)

    def test_refund_requires_review_state(self):
        self.assertIn('requires_review', PaymentRefund.Status.values)

    def test_payment_state_transitions_available(self):
        self.assertTrue({'created','pending','succeeded','failed','cancelled','expired'}.issubset(set(PaymentAttempt.Status.values)))
