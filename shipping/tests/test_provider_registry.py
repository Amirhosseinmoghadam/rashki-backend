from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from shipping.models import ShippingMethod
from shipping.providers.registry import get_shipping_provider
from shipping.providers.base import ShippingProviderUnavailableError
from shipping.providers.manual import ManualTariffProvider
from shipping.providers.tipax import TipaxProvider
from shipping.providers.post_pishtaz import PostPishtazProvider
from shipping.services import quote_shipping_method
from shipping.providers.base import ProviderQuote, ShippingProviderError


class ProviderRegistryTests(SimpleTestCase):
    def make_method(self, *, mode=None, provider=None):
        return SimpleNamespace(calculation_mode=mode, provider=provider)

    def test_manual_mode(self):
        method = self.make_method(mode=ShippingMethod.CalculationMode.MANUAL)
        self.assertIsInstance(get_shipping_provider(method), ManualTariffProvider)

    def test_tipax_provider(self):
        method = self.make_method(mode="api", provider=ShippingMethod.Provider.TIPAX)
        self.assertIsInstance(get_shipping_provider(method), TipaxProvider)

    def test_post_provider(self):
        method = self.make_method(mode="api", provider=ShippingMethod.Provider.POST)
        self.assertIsInstance(get_shipping_provider(method), PostPishtazProvider)

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(ShippingProviderUnavailableError):
            get_shipping_provider(self.make_method(mode="api", provider="unknown"))

    @patch("shipping.services.get_shipping_provider")
    def test_successful_quote_passes_all_parameters(self, get_provider):
        method, address, origin, packages = object(), object(), object(), [object()]
        get_provider.return_value.quote.return_value = ProviderQuote(amount_toman=60000, provider_data={"source": "test"})
        result = quote_shipping_method(method=method, destination_address=address, weight_grams=1200,
                                      package_value_toman=100000, packages=packages, origin=origin)
        self.assertTrue(result.is_available)
        self.assertEqual(result.amount_toman, 60000)
        self.assertEqual(result.provider_data, {"source": "test"})
        get_provider.return_value.quote.assert_called_once_with(
            method=method, destination_address=address, weight_grams=1200,
            package_value_toman=100000, packages=packages, origin=origin)

    @patch("shipping.services.get_shipping_provider")
    def test_provider_error_does_not_crash_all_quotes(self, get_provider):
        get_provider.return_value.quote.side_effect = ShippingProviderError("unavailable")
        result = quote_shipping_method(method=object(), destination_address=object(), weight_grams=800)
        self.assertFalse(result.is_available)
        self.assertIsNone(result.amount_toman)
        self.assertIn("unavailable", result.unavailable_reason)

    @patch("shipping.services.get_shipping_provider", side_effect=ShippingProviderUnavailableError("not configured"))
    def test_provider_lookup_error_returns_unavailable(self, _):
        result = quote_shipping_method(method=object(), destination_address=object(), weight_grams=400)
        self.assertFalse(result.is_available)
