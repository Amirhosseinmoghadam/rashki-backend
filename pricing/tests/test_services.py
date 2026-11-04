from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from pricing.services import (get_active_exchange_rate, ExchangeRateNotFoundError,
                              recalculate_product_price, activate_exchange_rate)
from .base import product_stub


class ExchangeLookupTests(SimpleTestCase):
    @patch("pricing.services.ExchangeRate.objects")
    def test_lookup_normalizes_currency(self, manager):
        expected = object()
        manager.filter.return_value.first.return_value = expected
        self.assertIs(get_active_exchange_rate(" usd "), expected)
        manager.filter.assert_called_once_with(currency="USD", is_active=True)

    @patch("pricing.services.ExchangeRate.objects")
    def test_missing_active_rate_raises(self, manager):
        manager.filter.return_value.first.return_value = None
        with self.assertRaises(ExchangeRateNotFoundError):
            get_active_exchange_rate("EUR")


class RecalculationUnitTests(SimpleTestCase):
    @patch("pricing.services.calculate_product_price")
    def test_locked_product_skipped(self, calculator):
        item = product_stub(is_price_locked=True)
        self.assertIsNone(recalculate_product_price(item))
        calculator.assert_not_called()

    @patch("pricing.services.Product.objects")
    @patch("pricing.services.calculate_product_price")
    def test_force_updates_locked_product(self, calculator, manager):
        item = product_stub(is_price_locked=True)
        calculator.return_value = SimpleNamespace(final_price_toman=120000, exchange_rate_toman=None)
        result = recalculate_product_price(item, force=True)
        self.assertEqual(result.final_price_toman, 120000)
        manager.filter.assert_called_once_with(pk=item.pk)
        self.assertEqual(manager.filter.return_value.update.call_args.kwargs["current_price_toman"], 120000)

    @patch("pricing.services.Product.objects")
    @patch("pricing.services.calculate_product_price")
    def test_recalculation_updates_in_memory_and_storage(self, calculator, manager):
        item = product_stub()
        calculator.return_value = SimpleNamespace(final_price_toman=123000, exchange_rate_toman=100000)
        recalculate_product_price(item)
        self.assertEqual(item.current_price_toman, 123000)
        self.assertEqual(item.last_exchange_rate_toman, 100000)
        self.assertIsNotNone(item.price_updated_at)
        self.assertEqual(manager.filter.return_value.update.call_args.kwargs["last_exchange_rate_toman"], 100000)
