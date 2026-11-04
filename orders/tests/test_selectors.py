from unittest.mock import patch
from django.test import SimpleTestCase
from orders.selectors import get_order_queryset, get_user_orders


class OrderSelectorsTests(SimpleTestCase):
    @patch('orders.selectors.Order.objects')
    def test_order_queryset_preloads_related_objects(self, objects):
        get_order_queryset()
        objects.select_related.assert_called_once_with('user', 'address', 'shipping_method', 'discount')

    @patch('orders.selectors.get_order_queryset')
    def test_user_orders_are_filtered_and_sorted(self, get_queryset):
        user = object()
        get_user_orders(user)
        get_queryset.return_value.filter.assert_called_once_with(user=user)
        get_queryset.return_value.filter.return_value.order_by.assert_called_once_with('-created_at')
