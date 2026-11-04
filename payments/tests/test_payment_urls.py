import uuid
from django.test import SimpleTestCase
from django.urls import reverse, resolve

class PaymentUrlTests(SimpleTestCase):
    def test_start_endpoint(self):
        url=reverse('payments_api_v1:payment-start')
        self.assertEqual(resolve(url).url_name, 'payment-start')

    def test_detail_endpoint(self):
        url=reverse('payments_api_v1:payment-detail', kwargs={'public_id':uuid.uuid4()})
        self.assertEqual(resolve(url).url_name, 'payment-detail')

    def test_zarinpal_callback_endpoint(self):
        url=reverse('payments_api_v1:zarinpal-callback', kwargs={'public_id':uuid.uuid4()})
        self.assertEqual(resolve(url).url_name, 'zarinpal-callback')

    def test_tcart_callback_endpoint(self):
        url=reverse('payments_api_v1:tcart-callback', kwargs={'public_id':uuid.uuid4()})
        self.assertEqual(resolve(url).url_name, 'tcart-callback')

    def test_refund_create_endpoint(self):
        url=reverse('payments_api_v1:refund-create')
        self.assertEqual(resolve(url).url_name, 'refund-create')

    def test_refund_detail_endpoint(self):
        url=reverse('payments_api_v1:refund-detail', kwargs={'public_id':uuid.uuid4()})
        self.assertEqual(resolve(url).url_name, 'refund-detail')

    def test_refund_execute_endpoint(self):
        url=reverse('payments_api_v1:refund-execute', kwargs={'public_id':uuid.uuid4()})
        self.assertEqual(resolve(url).url_name, 'refund-execute')
