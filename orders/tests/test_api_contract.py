from unittest.mock import patch
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from orders.api.v1.views import OrderListCreateAPIView, OrderDetailAPIView, OrderCancelAPIView
from django.contrib.auth.models import AnonymousUser


class FakeUser:
    is_authenticated = True
    is_active = True
    is_staff = False
    pk = 123


class OrderAPIContractTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_anonymous_list_denied(self):
        request = self.factory.get('/api/v1/orders/')
        response = OrderListCreateAPIView.as_view()(request)
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_create_denied(self):
        request = self.factory.post('/api/v1/orders/', {}, format='json')
        response = OrderListCreateAPIView.as_view()(request)
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_detail_denied(self):
        request = self.factory.get('/api/v1/orders/TEST/')
        response = OrderDetailAPIView.as_view()(request, order_number='TEST')
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cancel_denied(self):
        request = self.factory.post('/api/v1/orders/TEST/cancel/', {}, format='json')
        response = OrderCancelAPIView.as_view()(request, order_number='TEST')
        self.assertIn(response.status_code, (401, 403))

    @patch('orders.api.v1.views.create_order_from_cart')
    def test_invalid_checkout_does_not_call_service(self, create):
        request = self.factory.post('/api/v1/orders/', {'address_id': 0, 'shipping_method_id': 1, 'accept_terms': True}, format='json')
        force_authenticate(request, user=FakeUser())
        response = OrderListCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        create.assert_not_called()

    @patch('orders.api.v1.views.create_order_from_cart')
    def test_rejected_terms_does_not_call_service(self, create):
        request = self.factory.post('/api/v1/orders/', {'address_id': 1, 'shipping_method_id': 1, 'accept_terms': False}, format='json')
        force_authenticate(request, user=FakeUser())
        response = OrderListCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        create.assert_not_called()
