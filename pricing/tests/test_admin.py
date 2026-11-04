from unittest.mock import MagicMock, patch
from django.contrib import admin
from django.test import TestCase
from pricing.models import ExchangeRate, PricingSettings
from pricing.admin import ExchangeRateAdmin, PricingSettingsAdmin


class PricingAdminTests(TestCase):
    def test_both_models_registered(self):
        self.assertIn(ExchangeRate, admin.site._registry)
        self.assertIn(PricingSettings, admin.site._registry)

    def test_formatted_rate(self):
        instance = ExchangeRate(rate_toman=100000, currency="USD")
        model_admin = ExchangeRateAdmin(ExchangeRate, admin.site)
        self.assertEqual(model_admin.formatted_rate(instance), "100,000 تومان")

    def test_settings_admin_blocks_delete(self):
        model_admin = PricingSettingsAdmin(PricingSettings, admin.site)
        self.assertFalse(model_admin.has_delete_permission(MagicMock()))

    def test_settings_admin_blocks_second_add(self):
        PricingSettings.load()
        model_admin = PricingSettingsAdmin(PricingSettings, admin.site)
        self.assertFalse(model_admin.has_add_permission(MagicMock()))

    def test_rate_admin_rejects_multiple_selection(self):
        model_admin = ExchangeRateAdmin(ExchangeRate, admin.site)
        request = MagicMock()
        qs = MagicMock()
        qs.count.return_value = 2
        with patch.object(model_admin, "message_user") as message, patch("pricing.admin.activate_exchange_rate") as activate:
            model_admin.activate_rate_and_update_prices(request, qs)
        message.assert_called_once()
        activate.assert_not_called()
