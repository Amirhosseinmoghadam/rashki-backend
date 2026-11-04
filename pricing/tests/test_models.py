from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from pricing.models import ExchangeRate, PricingSettings


class ExchangeRateModelTests(TestCase):
    def test_currency_normalized(self):
        rate = ExchangeRate.objects.create(currency=" usd ", rate_toman=100000)
        self.assertEqual(rate.currency, "USD")

    def test_only_one_active_rate_for_same_currency(self):
        old = ExchangeRate.objects.create(currency="USD", rate_toman=90000, is_active=True)
        latest = ExchangeRate.objects.create(currency="USD", rate_toman=100000, is_active=True)
        old.refresh_from_db()
        self.assertFalse(old.is_active)
        self.assertTrue(latest.is_active)

    def test_independent_active_currencies(self):
        usd = ExchangeRate.objects.create(currency="USD", rate_toman=100000, is_active=True)
        eur = ExchangeRate.objects.create(currency="EUR", rate_toman=120000, is_active=True)
        self.assertTrue(usd.is_active)
        self.assertTrue(eur.is_active)

    def test_inactive_rate_keeps_existing_active(self):
        original = ExchangeRate.objects.create(currency="USD", rate_toman=100000, is_active=True)
        ExchangeRate.objects.create(currency="USD", rate_toman=110000, is_active=False)
        original.refresh_from_db()
        self.assertTrue(original.is_active)

    def test_rate_must_be_positive_on_validation(self):
        obj = ExchangeRate(currency="USD", rate_toman=0)
        with self.assertRaises(ValidationError):
            obj.full_clean()


class PricingSettingsModelTests(TestCase):
    def test_load_creates_singleton(self):
        a = PricingSettings.load()
        b = PricingSettings.load()
        self.assertEqual((a.pk, b.pk, PricingSettings.objects.count()), (1, 1, 1))

    def test_saving_second_object_updates_singleton(self):
        PricingSettings.load()
        PricingSettings(rounding_step_toman=10000, rounding_mode="up").save()
        self.assertEqual(PricingSettings.objects.count(), 1)
        self.assertEqual(PricingSettings.load().rounding_step_toman, 10000)

    def test_delete_is_disabled(self):
        instance = PricingSettings.load()
        instance.delete()
        self.assertTrue(PricingSettings.objects.filter(pk=1).exists())

    def test_rounding_step_validation(self):
        with self.assertRaises(ValidationError):
            PricingSettings(rounding_step_toman=0).full_clean()

    def test_default_rounding(self):
        obj = PricingSettings.load()
        self.assertEqual(obj.rounding_step_toman, 1000)
        self.assertEqual(obj.rounding_mode, PricingSettings.RoundingMode.NEAREST)
