from django.test import RequestFactory, SimpleTestCase, override_settings

from accounts.otp import (
    check_send_otp_rate_limit,
    generate_otp,
    get_client_ip,
    hash_otp,
    verify_otp_hash,
)


@override_settings(AUTH_OTP_LENGTH=6, AUTH_OTP_HMAC_KEY='test-only-secret')
class OTPHelperTests(SimpleTestCase):
    def test_generated_otp_has_fixed_numeric_length(self):
        code = generate_otp()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdecimal())

    def test_otp_hash_is_not_plaintext_and_can_be_verified(self):
        hashed = hash_otp('123456')
        self.assertNotEqual(hashed, '123456')
        self.assertTrue(verify_otp_hash('123456', hashed))
        self.assertFalse(verify_otp_hash('654321', hashed))

    @override_settings(AUTH_TRUST_X_FORWARDED_FOR=False)
    def test_ignores_forwarded_ip_by_default(self):
        request = RequestFactory().get('/', HTTP_X_FORWARDED_FOR='1.2.3.4', REMOTE_ADDR='127.0.0.9')
        self.assertEqual(get_client_ip(request), '127.0.0.9')

    @override_settings(AUTH_TRUST_X_FORWARDED_FOR=True)
    def test_uses_first_forwarded_ip_when_trusted(self):
        request = RequestFactory().get('/', HTTP_X_FORWARDED_FOR='1.2.3.4, 5.6.7.8')
        self.assertEqual(get_client_ip(request), '1.2.3.4')


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'accounts-test-otp'}},
    AUTH_OTP_RESEND_SECONDS=60,
    AUTH_OTP_MAX_SENDS_PER_HOUR=10,
    AUTH_OTP_MAX_SENDS_PER_IP_WINDOW=10,
    AUTH_OTP_IP_WINDOW_SECONDS=60,
)
class OTPRateLimitTests(SimpleTestCase):
    def test_immediate_resend_is_blocked(self):
        from django.core.cache import cache
        cache.clear()
        request = RequestFactory().get('/', REMOTE_ADDR='127.0.0.1')
        first = check_send_otp_rate_limit(request, '09123456789')
        second = check_send_otp_rate_limit(request, '09123456789')
        self.assertTrue(first['allowed'])
        self.assertFalse(second['allowed'])
        self.assertEqual(second['reason'], 'resend')
