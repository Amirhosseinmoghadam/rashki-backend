from unittest.mock import patch
from django.test import TestCase
from pricing.models import ExchangeRate
from pricing.services import activate_exchange_rate


class RateActivationTests(TestCase):
    @patch("pricing.services.recalculate_usd_products", return_value=4)
    def test_usd_activation_recalculates_products(self, recalculate):
        old = ExchangeRate.objects.create(currency="USD", rate_toman=90000, is_active=True)
        new = ExchangeRate.objects.create(currency="USD", rate_toman=100000, is_active=False)
        self.assertEqual(activate_exchange_rate(new), 4)
        old.refresh_from_db()
        new.refresh_from_db()
        self.assertFalse(old.is_active)
        self.assertTrue(new.is_active)
        recalculate.assert_called_once()
        self.assertEqual(recalculate.call_args.kwargs["exchange_rate"].pk, new.pk)

    @patch("pricing.services.recalculate_usd_products")
    def test_eur_activation_does_not_recalculate_usd(self, recalculate):
        rate = ExchangeRate.objects.create(currency="EUR", rate_toman=115000)
        self.assertEqual(activate_exchange_rate(rate), 0)
        rate.refresh_from_db()
        self.assertTrue(rate.is_active)
        recalculate.assert_not_called()

    @patch("pricing.services.recalculate_usd_products", side_effect=RuntimeError("recalc failed"))
    def test_activation_rolls_back_on_failure(self, recalculate):
        old = ExchangeRate.objects.create(currency="USD", rate_toman=90000, is_active=True)
        new = ExchangeRate.objects.create(currency="USD", rate_toman=100000, is_active=False)
        with self.assertRaises(RuntimeError):
            activate_exchange_rate(new)
        old.refresh_from_db()
        new.refresh_from_db()
        self.assertTrue(old.is_active)
        self.assertFalse(new.is_active)
