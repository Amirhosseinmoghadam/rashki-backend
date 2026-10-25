from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import OTPCode, User
from accounts.otp import hash_otp
from accounts.services import (
    ExpiredOTPError,
    InvalidOTPError,
    OTPCodeMismatchError,
    issue_auth_otp,
    verify_auth_otp,
)


@override_settings(AUTH_OTP_HMAC_KEY='test-only-secret', AUTH_OTP_EXPIRE_SECONDS=180, AUTH_OTP_MAX_ATTEMPTS=5)
class AccountServiceTests(TestCase):
    phone_number = '09123456789'

    def make_otp(self, code='123456', **kwargs):
        data = dict(
            phone_number=self.phone_number,
            code_hash=hash_otp(code),
            expires_at=timezone.now() + timedelta(minutes=3),
        )
        data.update(kwargs)
        return OTPCode.objects.create(**data)

    @patch('accounts.services.generate_otp', return_value='123456')
    @patch('accounts.services.send_auth_otp_sms', return_value={'debug_otp': None})
    def test_issue_auth_otp_invalidates_previous_codes(self, sender, generator):
        previous = self.make_otp()
        result = issue_auth_otp(phone_number=self.phone_number)
        previous.refresh_from_db()
        self.assertTrue(previous.is_used)
        self.assertEqual(OTPCode.objects.filter(phone_number=self.phone_number, is_used=False).count(), 1)
        self.assertEqual(result['expires_in'], 180)
        sender.assert_called_once()

    def test_verify_missing_otp_rejected(self):
        with self.assertRaises(InvalidOTPError):
            verify_auth_otp(phone_number=self.phone_number, otp_code='123456')

    def test_verify_expired_otp_marks_used(self):
        otp = self.make_otp(expires_at=timezone.now() - timedelta(seconds=1))
        with self.assertRaises(ExpiredOTPError):
            verify_auth_otp(phone_number=self.phone_number, otp_code='123456')
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_wrong_code_increments_attempts(self):
        otp = self.make_otp()
        with self.assertRaises(OTPCodeMismatchError) as caught:
            verify_auth_otp(phone_number=self.phone_number, otp_code='654321')
        otp.refresh_from_db()
        self.assertEqual(otp.attempts, 1)
        self.assertEqual(caught.exception.extra['remaining_attempts'], 4)

    def test_correct_otp_creates_verified_user_and_marks_used(self):
        otp = self.make_otp()
        verify_auth_otp(phone_number=self.phone_number, otp_code='123456')
        user = User.objects.get(phone_number=self.phone_number)
        self.assertTrue(user.is_phone_verified)
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
