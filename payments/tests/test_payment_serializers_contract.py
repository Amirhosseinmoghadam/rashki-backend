from django.test import SimpleTestCase
from payments.api.v1.serializers import (PaymentStartSerializer, PaymentRefundCreateSerializer, PaymentAttemptSerializer, PaymentRefundSerializer)

class PaymentSerializerTests(SimpleTestCase):
    def test_zarinpal_is_valid_choice(self):
        self.assertTrue(PaymentStartSerializer(data={'order_number':'ORD-1','provider':'zarinpal'}).is_valid())

    def test_tcart_is_valid_choice(self):
        self.assertTrue(PaymentStartSerializer(data={'order_number':'ORD-1','provider':'tcart'}).is_valid())

    def test_unknown_provider_rejected(self):
        self.assertFalse(PaymentStartSerializer(data={'order_number':'ORD-1','provider':'unknown'}).is_valid())

    def test_missing_order_number_rejected(self):
        self.assertFalse(PaymentStartSerializer(data={'provider':'zarinpal'}).is_valid())

    def test_refund_can_omit_amount(self):
        self.assertTrue(PaymentRefundCreateSerializer(data={'order_number':'ORD-1'}).is_valid())

    def test_refund_rejects_zero(self):
        self.assertFalse(PaymentRefundCreateSerializer(data={'order_number':'ORD-1','amount_toman':0}).is_valid())

    def test_refund_rejects_negative_amount(self):
        self.assertFalse(PaymentRefundCreateSerializer(data={'order_number':'ORD-1','amount_toman':-1}).is_valid())

    def test_refund_accepts_null_amount(self):
        self.assertTrue(PaymentRefundCreateSerializer(data={'order_number':'ORD-1','amount_toman':None}).is_valid())

    def test_refund_reason_limit(self):
        self.assertFalse(PaymentRefundCreateSerializer(data={'order_number':'ORD-1','reason':'x'*101}).is_valid())

    def test_refund_description_limit(self):
        self.assertFalse(PaymentRefundCreateSerializer(data={'order_number':'ORD-1','description':'x'*501}).is_valid())

    def test_attempt_serializer_is_read_only(self):
        s=PaymentAttemptSerializer()
        self.assertEqual(set(s.fields), set(s.Meta.read_only_fields))

    def test_refund_serializer_is_read_only(self):
        s=PaymentRefundSerializer()
        self.assertEqual(set(s.fields), set(s.Meta.read_only_fields))
