from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from products.models import Product
from pricing.services import (calculate_product_price, InvalidProductPriceError,
                              PriceCalculationResult)
from .base import product_stub, settings_stub


class CalculationTests(SimpleTestCase):
    def calculate(self, product, rate=None, settings=None):
        return calculate_product_price(product, exchange_rate=rate,
                                       pricing_settings=settings or settings_stub())

    def test_fixed_price_without_markup(self):
        result = self.calculate(product_stub(base_price_toman=100000))
        self.assertEqual(result.final_price_toman, 100000)
        self.assertIsNone(result.exchange_rate_toman)

    def test_fixed_markup_and_cost(self):
        result = self.calculate(product_stub(base_price_toman=100000, markup_percent=Decimal("20"), fixed_cost_toman=5000))
        self.assertEqual((result.base_price_toman, result.markup_amount_toman,
                          result.fixed_cost_toman, result.raw_price_toman,
                          result.final_price_toman), (100000, 20000, 5000, 125000, 125000))

    def test_fixed_rounding(self):
        result = self.calculate(product_stub(base_price_toman=123456), settings=settings_stub(10000))
        self.assertEqual(result.final_price_toman, 120000)

    def test_usd_conversion(self):
        item = product_stub(mode=Product.PricingMode.USD_BASED, base_price_usd=Decimal("12.50"))
        result = self.calculate(item, rate=SimpleNamespace(rate_toman=100000))
        self.assertEqual(result.base_price_toman, 1250000)
        self.assertEqual(result.exchange_rate_toman, 100000)

    def test_usd_markup_rounding(self):
        item = product_stub(mode=Product.PricingMode.USD_BASED,
                            base_price_usd=Decimal("1.5"), markup_percent=Decimal("10"), fixed_cost_toman=150)
        result = self.calculate(item, rate=SimpleNamespace(rate_toman=100000), settings=settings_stub(1000))
        self.assertEqual(result.raw_price_toman, 165150)
        self.assertEqual(result.final_price_toman, 165000)

    def test_usd_fetches_active_rate_when_not_supplied(self):
        item = product_stub(mode=Product.PricingMode.USD_BASED, base_price_usd=Decimal("2"))
        with patch("pricing.services.get_active_exchange_rate", return_value=SimpleNamespace(rate_toman=100000)) as get_rate:
            self.assertEqual(self.calculate(item).final_price_toman, 200000)
            get_rate.assert_called_once_with("USD")

    def test_fixed_does_not_query_exchange_rate(self):
        with patch("pricing.services.get_active_exchange_rate") as get_rate:
            self.calculate(product_stub())
            get_rate.assert_not_called()

    def test_missing_fixed_base(self):
        with self.assertRaises(InvalidProductPriceError):
            self.calculate(product_stub(base_price_toman=None))

    def test_missing_usd_base(self):
        with self.assertRaises(InvalidProductPriceError):
            self.calculate(product_stub(mode=Product.PricingMode.USD_BASED, base_price_usd=None), rate=SimpleNamespace(rate_toman=1))

    def test_invalid_pricing_mode(self):
        with self.assertRaises(InvalidProductPriceError):
            self.calculate(product_stub(mode="wrong"))

    def test_zero_final_raw_price(self):
        with self.assertRaises(InvalidProductPriceError):
            self.calculate(product_stub(base_price_toman=0))

    def test_result_type(self):
        self.assertIsInstance(self.calculate(product_stub()), PriceCalculationResult)
