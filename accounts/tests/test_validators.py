from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from accounts.validators import normalize_phone_number, validate_iran_mobile


class IranianMobileValidatorTests(SimpleTestCase):
    def test_normalize_trims_whitespace(self):
        self.assertEqual(normalize_phone_number(' 09123456789 '), '09123456789')

    def test_accepts_valid_number(self):
        self.assertEqual(validate_iran_mobile('09123456789'), '09123456789')

    def test_rejects_invalid_numbers(self):
        for number in ('', '9123456789', '08123456789', '0912345678', '091234567890', 'abcdefghijk'):
            with self.subTest(number=number):
                with self.assertRaises(ValidationError):
                    validate_iran_mobile(number)
