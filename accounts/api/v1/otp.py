import hashlib
import hmac
import secrets

from django.conf import settings
from django.core.cache import cache

# =========================================================
# OTP Generation
# =========================================================


def generate_otp():
    """
    Cryptographically secure numeric OTP.
    """

    length = settings.AUTH_OTP_LENGTH

    minimum = 10 ** (length - 1)
    maximum = (10**length) - 1

    return str(secrets.randbelow(maximum - minimum + 1) + minimum)


# =========================================================
# OTP Hash
# =========================================================


def hash_otp(otp_code):
    """
    HMAC-SHA256 instead of plain SHA256.

    The OTP itself is never stored.
    """

    secret = settings.SECRET_KEY.encode("utf-8")

    message = otp_code.encode("utf-8")

    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).hexdigest()


# =========================================================
# OTP Compare
# =========================================================


def verify_otp_hash(
    otp_code,
    stored_hash,
):
    """
    Constant-time comparison.
    """

    calculated_hash = hash_otp(otp_code)

    return hmac.compare_digest(
        calculated_hash,
        stored_hash,
    )


# =========================================================
# Cache Counter
# =========================================================


def increment_counter(
    key,
    timeout,
):
    """
    Increment a Redis/cache counter.

    The first request creates the key.
    """

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


# =========================================================
# Client IP
# =========================================================


def get_client_ip(request):
    """
    Get client IP.

    IMPORTANT:
    HTTP_X_FORWARDED_FOR should only be trusted
    when your reverse proxy is configured correctly.

    By default REMOTE_ADDR is safer.
    """

    return request.META.get(
        "REMOTE_ADDR",
        "unknown",
    )


# =========================================================
# Send OTP Rate Limit
# =========================================================


def check_send_otp_rate_limit(
    request,
    phone_number,
):
    """
    Limits:

    Phone:
        1 request / 60 seconds
        5 requests / hour

    IP:
        30 requests / 10 minutes
    """

    ip = get_client_ip(request)

    # -----------------------------------------------------
    # Phone - resend
    # -----------------------------------------------------

    resend_key = f"auth:otp:resend:{phone_number}"

    if cache.get(resend_key):
        return {
            "allowed": False,
            "retry_after": (settings.AUTH_OTP_RESEND_SECONDS),
            "reason": "resend",
        }

    # -----------------------------------------------------
    # Phone - hourly
    # -----------------------------------------------------

    hourly_key = f"auth:otp:send:hour:{phone_number}"

    hourly_count = cache.get(
        hourly_key,
        0,
    )

    if hourly_count >= settings.AUTH_OTP_MAX_SENDS_PER_HOUR:
        return {
            "allowed": False,
            "retry_after": 3600,
            "reason": "phone_hourly",
        }

    # -----------------------------------------------------
    # IP
    # -----------------------------------------------------

    ip_key = f"auth:otp:send:ip:{ip}"

    ip_count = cache.get(
        ip_key,
        0,
    )

    if ip_count >= settings.AUTH_OTP_MAX_SENDS_PER_IP_WINDOW:
        return {
            "allowed": False,
            "retry_after": (settings.AUTH_OTP_IP_WINDOW_SECONDS),
            "reason": "ip",
        }

    # -----------------------------------------------------
    # Increment counters
    # -----------------------------------------------------

    cache.add(
        resend_key,
        True,
        timeout=(settings.AUTH_OTP_RESEND_SECONDS),
    )

    increment_counter(
        hourly_key,
        timeout=3600,
    )

    increment_counter(
        ip_key,
        timeout=(settings.AUTH_OTP_IP_WINDOW_SECONDS),
    )

    return {
        "allowed": True,
    }


# =========================================================
# Verify OTP Rate Limit
# =========================================================


def check_verify_otp_rate_limit(
    request,
    phone_number,
):
    """
    Verification attempts are also rate limited.

    Phone:
        AUTH_OTP_MAX_VERIFY_PER_WINDOW

    IP:
        AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW
    """

    ip = get_client_ip(request)

    phone_key = f"auth:otp:verify:phone:" f"{phone_number}"

    phone_count = cache.get(
        phone_key,
        0,
    )

    if phone_count >= settings.AUTH_OTP_MAX_VERIFY_PER_WINDOW:
        return {
            "allowed": False,
            "retry_after": (settings.AUTH_OTP_VERIFY_WINDOW_SECONDS),
        }

    ip_key = f"auth:otp:verify:ip:{ip}"

    ip_count = cache.get(
        ip_key,
        0,
    )

    if ip_count >= settings.AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW:
        return {
            "allowed": False,
            "retry_after": (settings.AUTH_OTP_VERIFY_IP_WINDOW_SECONDS),
        }

    increment_counter(
        phone_key,
        timeout=(settings.AUTH_OTP_VERIFY_WINDOW_SECONDS),
    )

    increment_counter(
        ip_key,
        timeout=(settings.AUTH_OTP_VERIFY_IP_WINDOW_SECONDS),
    )

    return {
        "allowed": True,
    }
