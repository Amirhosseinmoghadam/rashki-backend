from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from orders.models import Order
from payments.models import PaymentAttempt
from payments.services import _set_order_payment_status, process_payment_callback, PaymentNotFoundError

class PaymentServiceUnitTests(SimpleTestCase):
    def test_paid_order_cannot_be_set_failed(self):
        obj=SimpleNamespace(payment_status=Order.PaymentStatus.PAID, save=lambda **kwargs: self.fail('must not save'))
        _set_order_payment_status(obj, Order.PaymentStatus.FAILED)
        self.assertEqual(obj.payment_status, Order.PaymentStatus.PAID)

    def test_unpaid_order_can_be_set_pending(self):
        calls=[]
        obj=SimpleNamespace(payment_status=Order.PaymentStatus.FAILED, save=lambda **kwargs: calls.append(kwargs))
        _set_order_payment_status(obj, Order.PaymentStatus.PENDING)
        self.assertEqual(obj.payment_status, Order.PaymentStatus.PENDING)
        self.assertEqual(len(calls), 1)

    @patch('payments.services.get_payment_attempt_queryset')
    def test_unknown_callback_attempt_rejected(self, queryset):
        queryset.return_value.filter.return_value.first.return_value=None
        with self.assertRaises(PaymentNotFoundError):
            process_payment_callback(public_id='not-found',provider_key='tcart',callback_data={})

    @patch('payments.services.get_payment_provider')
    @patch('payments.services.get_payment_attempt_queryset')
    def test_duplicate_success_callback_is_idempotent(self, queryset, factory):
        attempt=SimpleNamespace(status=PaymentAttempt.Status.SUCCEEDED)
        queryset.return_value.filter.return_value.first.return_value=attempt
        result=process_payment_callback(public_id='id',provider_key='tcart',callback_data={})
        self.assertIs(result, attempt)
        factory.assert_not_called()
