import re
from unittest.mock import patch
from django.test import SimpleTestCase
from orders.services import generate_order_number


class OrderNumberTests(SimpleTestCase):
    @patch('orders.services.Order.objects.filter')
    def test_format(self, filter_):
        filter_.return_value.exists.return_value = False
        value = generate_order_number()
        self.assertRegex(value, r'^RK-\d{8}-[A-F0-9]{8}$')

    @patch('orders.services.Order.objects.filter')
    def test_check_for_existing_number(self, filter_):
        filter_.return_value.exists.return_value = False
        result = generate_order_number()
        filter_.assert_called_once_with(order_number=result)

    @patch('orders.services.Order.objects.filter')
    def test_collision_is_retried(self, filter_):
        filter_.return_value.exists.side_effect = [True, False]
        result = generate_order_number()
        self.assertRegex(result, r'^RK-\d{8}-[A-F0-9]{8}$')
        self.assertEqual(filter_.call_count, 2)
