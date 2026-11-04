from types import SimpleNamespace
from unittest.mock import patch
from django.test import TestCase
from products.models import Product
from pricing.models import PricingSettings
from pricing.services import recalculate_usd_products, recalculate_fixed_products
from .base import product_stub


class BatchRecalculationTests(TestCase):
    def setUp(self):
        PricingSettings.load()

    @patch("pricing.services.calculate_product_price")
    @patch("pricing.services.Product.objects")
    def test_usd_batches_and_count(self, manager, calculator):
        products = [product_stub(pk=i) for i in range(3)]
        manager.filter.return_value.exclude.return_value.order_by.return_value.iterator.return_value = iter(products)
        calculator.side_effect = [SimpleNamespace(final_price_toman=1000+i) for i in range(3)]
        count = recalculate_usd_products(exchange_rate=SimpleNamespace(rate_toman=100000), batch_size=2)
        self.assertEqual(count, 3)
        self.assertEqual(manager.bulk_update.call_count, 2)
        self.assertEqual([p.current_price_toman for p in products], [1000, 1001, 1002])

    @patch("pricing.services.calculate_product_price")
    @patch("pricing.services.Product.objects")
    def test_fixed_batches_and_count(self, manager, calculator):
        products = [product_stub(pk=i) for i in range(2)]
        manager.filter.return_value.exclude.return_value.order_by.return_value.iterator.return_value = iter(products)
        calculator.return_value = SimpleNamespace(final_price_toman=200000)
        count = recalculate_fixed_products(batch_size=1)
        self.assertEqual(count, 2)
        self.assertEqual(manager.bulk_update.call_count, 2)
        self.assertTrue(all(p.last_exchange_rate_toman is None for p in products))

    @patch("pricing.services.Product.objects")
    def test_usd_empty_queryset_returns_zero(self, manager):
        manager.filter.return_value.exclude.return_value.order_by.return_value.iterator.return_value = iter([])
        self.assertEqual(recalculate_usd_products(exchange_rate=SimpleNamespace(rate_toman=100000)), 0)
        manager.bulk_update.assert_not_called()

    @patch("pricing.services.Product.objects")
    def test_fixed_empty_queryset_returns_zero(self, manager):
        manager.filter.return_value.exclude.return_value.order_by.return_value.iterator.return_value = iter([])
        self.assertEqual(recalculate_fixed_products(), 0)
        manager.bulk_update.assert_not_called()
