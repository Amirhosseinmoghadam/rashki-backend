import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)


class OTPDeliveryError(Exception):
    pass


def send_auth_otp_sms(
    *,
    phone_number,
    otp_code,
):
    """
    ارسال OTP با Backend قابل تنظیم.

    AUTH_OTP_SENDER نمونه:
        "myapp.sms.send_otp"

    callable باید keywordهای phone_number و code را بپذیرد.
    """

    sender_path = getattr(
        settings,
        "AUTH_OTP_SENDER",
        "",
    )

    if sender_path:
        try:
            sender = import_string(
                sender_path
            )

            sender(
                phone_number=phone_number,
                code=otp_code,
            )

            return {
                "delivered": True,
                "debug_otp": None,
            }

        except Exception as exc:
            raise OTPDeliveryError(
                "ارسال پیامک تایید ناموفق بود."
            ) from exc

    if settings.DEBUG:
        debug_code_enabled = getattr(
            settings,
            "AUTH_OTP_DEBUG_RETURN_CODE",
            False,
        )

        logger.warning(
            (
                "AUTH_OTP_SENDER تنظیم نشده است؛ "
                "در حالت DEBUG پیامک واقعی ارسال نشد."
            )
        )

        return {
            "delivered": False,
            "debug_otp": (
                otp_code
                if debug_code_enabled
                else None
            ),
        }

    raise ImproperlyConfigured(
        "AUTH_OTP_SENDER must be configured in production."
    )
