from django.test import SimpleTestCase
from orders.api.v1.serializers import OrderCreateSerializer, OrderCancellationRequestSerializer


class OrderSerializerTests(SimpleTestCase):
    def test_valid_create_payload(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'shipping_method_id': 2, 'accept_terms': True, 'customer_note': 'OK'})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_terms_are_required(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'shipping_method_id': 2, 'accept_terms': False})
        self.assertFalse(serializer.is_valid())
        self.assertIn('accept_terms', serializer.errors)

    def test_address_id_must_be_positive(self):
        serializer = OrderCreateSerializer(data={'address_id': 0, 'shipping_method_id': 2, 'accept_terms': True})
        self.assertFalse(serializer.is_valid())
        self.assertIn('address_id', serializer.errors)

    def test_shipping_method_id_must_be_positive(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'shipping_method_id': 0, 'accept_terms': True})
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping_method_id', serializer.errors)

    def test_missing_required_field(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'accept_terms': True})
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping_method_id', serializer.errors)

    def test_customer_note_length(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'shipping_method_id': 2, 'accept_terms': True, 'customer_note': 'a' * 1001})
        self.assertFalse(serializer.is_valid())
        self.assertIn('customer_note', serializer.errors)

    def test_optional_customer_note(self):
        serializer = OrderCreateSerializer(data={'address_id': 1, 'shipping_method_id': 2, 'accept_terms': True})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_cancel_defaults(self):
        serializer = OrderCancellationRequestSerializer(data={})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['reason'], 'customer_request')
        self.assertEqual(serializer.validated_data['description'], '')

    def test_cancel_reason_length(self):
        serializer = OrderCancellationRequestSerializer(data={'reason': 'r' * 101})
        self.assertFalse(serializer.is_valid())
        self.assertIn('reason', serializer.errors)

    def test_cancel_description_length(self):
        serializer = OrderCancellationRequestSerializer(data={'description': 'x' * 501})
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)
