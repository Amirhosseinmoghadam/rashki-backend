from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from shipping.providers.manual import ManualTariffProvider
from shipping.providers.base import ShippingRateNotFoundError


class ManualTariffTests(SimpleTestCase):
    def setUp(self):
        self.provider = ManualTariffProvider()

    @patch.object(ManualTariffProvider, "_get_rule")
    def test_included_weight_has_no_surcharge(self, get_rule):
        get_rule.return_value = SimpleNamespace(id=1, included_weight_grams=1000,
            base_price_toman=20000, additional_per_kg_toman=7000)
        quote = self.provider.quote(method=object(), destination_address=object(), weight_grams=1000)
        self.assertEqual(quote.amount_toman, 20000)
        self.assertEqual(quote.provider_data["extra_kilos"], 0)

    @patch.object(ManualTariffProvider, "_get_rule")
    def test_partial_extra_kilo_is_rounded_up(self, get_rule):
        get_rule.return_value = SimpleNamespace(id=3, included_weight_grams=1000,
            base_price_toman=20000, additional_per_kg_toman=7000)
        quote = self.provider.quote(method=object(), destination_address=object(), weight_grams=1001)
        self.assertEqual(quote.amount_toman, 27000)
        self.assertEqual(quote.provider_data["extra_kilos"], 1)

    @patch.object(ManualTariffProvider, "_get_rule")
    def test_multiple_extra_kilos(self, get_rule):
        get_rule.return_value = SimpleNamespace(id=3, included_weight_grams=1000,
            base_price_toman=20000, additional_per_kg_toman=7000)
        quote = self.provider.quote(method=object(), destination_address=object(), weight_grams=3001)
        self.assertEqual(quote.amount_toman, 41000)
        self.assertEqual(quote.provider_data["extra_kilos"], 3)

    @patch.object(ManualTariffProvider, "_get_rule", side_effect=ShippingRateNotFoundError("no rule"))
    def test_missing_tariff_error(self, _):
        with self.assertRaises(ShippingRateNotFoundError):
            self.provider.quote(method=object(), destination_address=object(), weight_grams=1000)
