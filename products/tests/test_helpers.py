from decimal import Decimal
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError
from products.api.v1.views import parse_positive_int, parse_decimal

class ProductFilterHelperTests(SimpleTestCase):
    def test_empty_integer_filter(self):
        self.assertIsNone(parse_positive_int("", "stock"))

    def test_persian_digits(self):
        self.assertEqual(parse_positive_int("۱۲۳", "stock"), 123)

    def test_zero_integer_filter(self):
        self.assertEqual(parse_positive_int("0", "stock"), 0)

    def test_negative_filter_rejected(self):
        with self.assertRaises(ValidationError):
            parse_positive_int("-2", "stock")

    def test_text_filter_rejected(self):
        with self.assertRaises(ValidationError):
            parse_positive_int("abc", "stock")

    def test_decimal_filter(self):
        self.assertEqual(parse_decimal("12.5", "price"), Decimal("12.5"))

    def test_invalid_decimal_rejected(self):
        with self.assertRaises(ValidationError):
            parse_decimal("bad", "price")

    def test_empty_decimal(self):
        self.assertIsNone(parse_decimal(None, "price"))
