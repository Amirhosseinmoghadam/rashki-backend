import hashlib
import hmac
import secrets

from django.conf import settings
from django.core.cache import cache


def generate_otp():
    length = settings.AUTH_OTP_LENGTH

    minimum = 10 ** (length - 1)
    maximum = (10 ** length) - 1

    return str(
        secrets.randbelow(
            maximum - minimum + 1
        )
        + minimum
    )


def hash_otp(otp_code):
    secret = settings.AUTH_OTP_HMAC_KEY.encode("utf-8")
    message = otp_code.encode("utf-8")

    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_otp_hash(
    otp_code,
    stored_hash,
):
    return hmac.compare_digest(
        hash_otp(otp_code),
        stored_hash,
    )


def increment_counter(
    key,
    timeout,
):
    created = cache.add(
        key,
        1,
        timeout=timeout,
    )

    if created:
        return 1

    try:
        return cache.incr(key)
    except ValueError:
        cache.set(
            key,
            1,
            timeout=timeout,
        )
        return 1


def get_client_ip(request):
    trust_forwarded = getattr(
        settings,
        "AUTH_TRUST_X_FORWARDED_FOR",
        False,
    )

    if trust_forwarded:
        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR",
            "",
        )

        if forwarded:
            return forwarded.split(",")[0].strip()

    return request.META.get(
        "REMOTE_ADDR",
        "unknown",
    )


def check_send_otp_rate_limit(
    request,
    phone_number,
):
    ip = get_client_ip(request)

    resend_key = (
        f"auth:otp:resend:{phone_number}"
    )

    if cache.get(resend_key):
        return {
            "allowed": False,
            "retry_after": (
                settings.AUTH_OTP_RESEND_SECONDS
            ),
            "reason": "resend",
        }

    hourly_key = (
        f"auth:otp:send:hour:{phone_number}"
    )

    hourly_count = cache.get(
        hourly_key,
        0,
    )

    if (
        hourly_count
        >= settings.AUTH_OTP_MAX_SENDS_PER_HOUR
    ):
        return {
            "allowed": False,
            "retry_after": 3600,
            "reason": "phone_hourly",
        }

    ip_key = f"auth:otp:send:ip:{ip}"

    ip_count = cache.get(
        ip_key,
        0,
    )

    if (
        ip_count
        >= settings.AUTH_OTP_MAX_SENDS_PER_IP_WINDOW
    ):
        return {
            "allowed": False,
            "retry_after": (
                settings.AUTH_OTP_IP_WINDOW_SECONDS
            ),
            "reason": "ip",
        }

    cache.add(
        resend_key,
        True,
        timeout=settings.AUTH_OTP_RESEND_SECONDS,
    )

    increment_counter(
        hourly_key,
        timeout=3600,
    )

    increment_counter(
        ip_key,
        timeout=settings.AUTH_OTP_IP_WINDOW_SECONDS,
    )

    return {
        "allowed": True,
    }


def check_verify_otp_rate_limit(
    request,
    phone_number,
):
    ip = get_client_ip(request)

    phone_key = (
        "auth:otp:verify:phone:"
        f"{phone_number}"
    )

    phone_count = cache.get(
        phone_key,
        0,
    )

    if (
        phone_count
        >= settings.AUTH_OTP_MAX_VERIFY_PER_WINDOW
    ):
        return {
            "allowed": False,
            "retry_after": (
                settings.AUTH_OTP_VERIFY_WINDOW_SECONDS
            ),
            "reason": "phone",
        }

    ip_key = (
        f"auth:otp:verify:ip:{ip}"
    )

    ip_count = cache.get(
        ip_key,
        0,
    )

    if (
        ip_count
        >= settings.AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW
    ):
        return {
            "allowed": False,
            "retry_after": (
                settings.AUTH_OTP_VERIFY_IP_WINDOW_SECONDS
            ),
            "reason": "ip",
        }

    increment_counter(
        phone_key,
        timeout=settings.AUTH_OTP_VERIFY_WINDOW_SECONDS,
    )

    increment_counter(
        ip_key,
        timeout=settings.AUTH_OTP_VERIFY_IP_WINDOW_SECONDS,
    )

    return {
        "allowed": True,
    }
