from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import OTPCode


class UserModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_user_defaults_and_display(self):
        user = self.User.objects.create_user(phone_number='09123456789')
        self.assertEqual(str(user), '09123456789')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_phone_verified)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_profile_completed)

    def test_profile_name_helpers(self):
        user = self.User.objects.create_user(
            phone_number='09123456789', first_name='Ali', last_name='Ahmadi'
        )
        self.assertEqual(user.get_full_name(), 'Ali Ahmadi')
        self.assertEqual(user.full_name, 'Ali Ahmadi')
        self.assertEqual(user.get_short_name(), 'Ali')
        self.assertTrue(user.is_profile_completed)

    def test_phone_number_is_unique(self):
        self.User.objects.create_user(phone_number='09123456789')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.User.objects.create_user(phone_number='09123456789')


class OTPCodeModelTests(TestCase):
    def make_otp(self, **overrides):
        data = {
            'phone_number': '09123456789',
            'code_hash': 'hashed-code',
            'expires_at': timezone.now() + timedelta(minutes=3),
        }
        data.update(overrides)
        return OTPCode.objects.create(**data)

    def test_new_otp_is_valid(self):
        otp = self.make_otp()
        self.assertTrue(otp.is_valid)
        self.assertFalse(otp.is_expired)
        self.assertEqual(otp.attempts, 0)
        self.assertEqual(otp.purpose, OTPCode.OTPPurpose.AUTH)

    def test_expired_otp_is_invalid(self):
        otp = self.make_otp(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertTrue(otp.is_expired)
        self.assertFalse(otp.is_valid)

    def test_used_otp_is_invalid(self):
        self.assertFalse(self.make_otp(is_used=True).is_valid)

    def test_max_attempts_invalidates_otp(self):
        self.assertFalse(self.make_otp(attempts=5, max_attempts=5).is_valid)
