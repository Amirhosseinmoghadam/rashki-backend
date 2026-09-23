from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import OTPCode
from accounts.otp import hash_otp


@override_settings(
    AUTH_OTP_LENGTH=6,
    AUTH_OTP_EXPIRE_SECONDS=120,
    AUTH_OTP_MAX_ATTEMPTS=5,
    AUTH_OTP_RESEND_SECONDS=60,
    AUTH_OTP_MAX_SENDS_PER_HOUR=5,
    AUTH_OTP_MAX_SENDS_PER_IP_WINDOW=30,
    AUTH_OTP_IP_WINDOW_SECONDS=600,
    AUTH_OTP_MAX_VERIFY_PER_WINDOW=10,
    AUTH_OTP_VERIFY_WINDOW_SECONDS=300,
    AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW=30,
    AUTH_OTP_VERIFY_IP_WINDOW_SECONDS=300,
    AUTH_OTP_HMAC_KEY="test-hmac-key",
    AUTH_PHONE_REGEX_PATTERN=r"^09\d{9}$",
    AUTH_OTP_SENDER="",
    AUTH_OTP_DEBUG_RETURN_CODE=True,
)
class AccountsAuthAPITests(APITestCase):
    def setUp(self):
        cache.clear()

    def _create_otp(
        self,
        *,
        phone_number,
        code="123456",
        expired=False,
    ):
        expires_at = (
            timezone.now()
            - timedelta(seconds=1)
            if expired
            else timezone.now()
            + timedelta(minutes=2)
        )

        return OTPCode.objects.create(
            phone_number=phone_number,
            code_hash=hash_otp(code),
            purpose=OTPCode.OTPPurpose.AUTH,
            expires_at=expires_at,
            max_attempts=5,
        )

    def test_new_user_verify_creates_unusable_password_and_tokens(self):
        phone = "09120000001"
        self._create_otp(
            phone_number=phone,
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:verify-otp"
            ),
            {
                "phone_number": phone,
                "otp_code": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["success"]
        )

        user = get_user_model().objects.get(
            phone_number=phone
        )

        self.assertTrue(
            user.is_phone_verified
        )

        self.assertFalse(
            user.has_usable_password()
        )

        self.assertTrue(
            response.data["data"][
                "is_new_user"
            ]
        )

        self.assertIn(
            "access",
            response.data["data"]["tokens"],
        )

        self.assertIn(
            "refresh",
            response.data["data"]["tokens"],
        )

    def test_inactive_user_cannot_receive_jwt_after_valid_otp(self):
        User = get_user_model()

        user = User.objects.create_user(
            phone_number="09120000002",
            is_active=False,
            is_phone_verified=True,
        )

        self._create_otp(
            phone_number=user.phone_number,
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:verify-otp"
            ),
            {
                "phone_number": (
                    user.phone_number
                ),
                "otp_code": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertEqual(
            response.data["errors"]["code"],
            "inactive_user",
        )

        self.assertNotIn(
            "tokens",
            response.data,
        )

    def test_wrong_otp_increments_attempts(self):
        phone = "09120000003"

        otp = self._create_otp(
            phone_number=phone,
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:verify-otp"
            ),
            {
                "phone_number": phone,
                "otp_code": "654321",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        otp.refresh_from_db()

        self.assertEqual(
            otp.attempts,
            1,
        )

        self.assertEqual(
            response.data["errors"][
                "remaining_attempts"
            ],
            4,
        )

    def test_expired_otp_is_invalidated(self):
        phone = "09120000004"

        otp = self._create_otp(
            phone_number=phone,
            expired=True,
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:verify-otp"
            ),
            {
                "phone_number": phone,
                "otp_code": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        otp.refresh_from_db()

        self.assertTrue(
            otp.is_used
        )

    @patch(
        "accounts.api.v1.views.generate_otp",
        return_value="123456",
    )
    def test_send_otp_invalidates_previous_active_otp(
        self,
        mocked_generate,
    ):
        phone = "09120000005"

        old_otp = self._create_otp(
            phone_number=phone,
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:send-otp"
            ),
            {
                "phone_number": phone,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        old_otp.refresh_from_db()

        self.assertTrue(
            old_otp.is_used
        )

        active = OTPCode.objects.filter(
            phone_number=phone,
            is_used=False,
        )

        self.assertEqual(
            active.count(),
            1,
        )

        mocked_generate.assert_called_once_with()

        self.assertNotIn(
            "debug_otp",
            response.data["data"],
        )

    def test_logout_rejects_refresh_token_from_another_user(self):
        User = get_user_model()

        user1 = User.objects.create_user(
            phone_number="09120000006",
            is_phone_verified=True,
        )

        user2 = User.objects.create_user(
            phone_number="09120000007",
            is_phone_verified=True,
        )

        foreign_refresh = RefreshToken.for_user(
            user2
        )

        self.client.force_authenticate(
            user=user1
        )

        response = self.client.post(
            reverse(
                "accounts_api_v1:logout"
            ),
            {
                "refresh": str(
                    foreign_refresh
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            response.data["errors"]["code"],
            "token_owner_mismatch",
        )

    def test_me_returns_authenticated_user(self):
        User = get_user_model()

        user = User.objects.create_user(
            phone_number="09120000008",
            first_name="امیر",
            last_name="مقدم",
            is_phone_verified=True,
        )

        self.client.force_authenticate(
            user=user
        )

        response = self.client.get(
            reverse(
                "accounts_api_v1:me"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["data"][
                "phone_number"
            ],
            user.phone_number,
        )

        self.assertTrue(
            response.data["data"][
                "is_profile_completed"
            ]
        )
