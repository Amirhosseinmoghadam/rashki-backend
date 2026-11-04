from decimal import Decimal
from django.test import SimpleTestCase
from pricing.services import PricingError, round_toman
from pricing.models import PricingSettings


class RoundingTests(SimpleTestCase):
    def test_nearest_down(self):
        self.assertEqual(round_toman(1234, 100, "nearest"), 1200)

    def test_nearest_up(self):
        self.assertEqual(round_toman(1250, 100, "nearest"), 1300)

    def test_up(self):
        self.assertEqual(round_toman(1201, 100, "up"), 1300)

    def test_down(self):
        self.assertEqual(round_toman(1299, 100, "down"), 1200)

    def test_exact_step(self):
        for mode in PricingSettings.RoundingMode.values:
            with self.subTest(mode=mode):
                self.assertEqual(round_toman(1200, 100, mode), 1200)

    def test_decimal_precision(self):
        self.assertEqual(round_toman(Decimal("1.25"), Decimal("0.1"), "nearest"), 1)

    def test_zero_step(self):
        with self.assertRaises(PricingError):
            round_toman(100, 0, "nearest")

    def test_negative_step(self):
        with self.assertRaises(PricingError):
            round_toman(100, -10, "nearest")

    def test_invalid_mode(self):
        with self.assertRaises(PricingError):
            round_toman(100, 10, "sideways")
