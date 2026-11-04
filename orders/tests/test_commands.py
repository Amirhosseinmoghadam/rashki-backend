from io import StringIO
from unittest.mock import patch
from django.core.management import call_command
from django.test import SimpleTestCase


class ExpireUnpaidOrdersCommandTests(SimpleTestCase):
    @patch('orders.management.commands.expire_unpaid_orders.Order.objects')
    def test_command_without_candidates(self, objects):
        queryset = objects.filter.return_value.order_by.return_value
        queryset.count.return_value = 0
        queryset.iterator.return_value = iter([])
        output = StringIO()
        call_command('expire_unpaid_orders', stdout=output)
        self.assertIn('Candidates: 0', output.getvalue())
        self.assertIn('Errors: 0', output.getvalue())

    @patch('orders.management.commands.expire_unpaid_orders.expire_unpaid_order')
    @patch('orders.management.commands.expire_unpaid_orders.Order.objects')
    def test_command_counts_expired(self, objects, expire):
        from orders.models import Order
        order = type('FakeOrder', (), {'order_number': 'TEST-1'})()
        queryset = objects.filter.return_value.order_by.return_value
        queryset.count.return_value = 1
        queryset.iterator.return_value = iter([order])
        expire.return_value.status = Order.Status.EXPIRED
        output = StringIO()
        call_command('expire_unpaid_orders', stdout=output)
        expire.assert_called_once_with(order)
        self.assertIn('Expired: 1', output.getvalue())

    @patch('orders.management.commands.expire_unpaid_orders.expire_unpaid_order')
    @patch('orders.management.commands.expire_unpaid_orders.Order.objects')
    def test_command_reports_errors_without_crashing(self, objects, expire):
        order = type('FakeOrder', (), {'order_number': 'TEST-1'})()
        queryset = objects.filter.return_value.order_by.return_value
        queryset.count.return_value = 1
        queryset.iterator.return_value = iter([order])
        expire.side_effect = RuntimeError('test failure')
        out, err = StringIO(), StringIO()
        call_command('expire_unpaid_orders', stdout=out, stderr=err)
        self.assertIn('Errors: 1', out.getvalue())
        self.assertIn('TEST-1', err.getvalue())
