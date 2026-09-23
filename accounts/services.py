from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import OTPCode, User
from accounts.otp import (
    generate_otp,
    hash_otp,
    verify_otp_hash,
)
from accounts.sms import (
    OTPDeliveryError,
    send_auth_otp_sms,
)


class AccountServiceError(Exception):
    status_code = 400
    error_code = "account_error"

    def __init__(
        self,
        message,
        *,
        extra=None,
    ):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}


class InvalidOTPError(AccountServiceError):
    error_code = "invalid_otp"


class ExpiredOTPError(AccountServiceError):
    error_code = "expired_otp"


class OTPAttemptsExceededError(AccountServiceError):
    status_code = 429
    error_code = "otp_attempts_exceeded"


class OTPCodeMismatchError(AccountServiceError):
    error_code = "otp_code_mismatch"


class InactiveUserError(AccountServiceError):
    status_code = 403
    error_code = "inactive_user"


class OTPDeliveryServiceError(AccountServiceError):
    status_code = 503
    error_code = "otp_delivery_failed"


def create_tokens(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_user_data(user):
    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_phone_verified": user.is_phone_verified,
        "is_profile_completed": user.is_profile_completed,
    }


def issue_auth_otp(
    *,
    phone_number,
):
    """
    OTP جدید ایجاد می‌کند و OTPهای فعال قبلی Auth
    برای همان شماره را invalidate می‌کند.
    """

    otp_code = generate_otp()

    expires_at = (
        timezone.now()
        + timedelta(
            seconds=settings.AUTH_OTP_EXPIRE_SECONDS
        )
    )

    with transaction.atomic():
        OTPCode.objects.filter(
            phone_number=phone_number,
            purpose=OTPCode.OTPPurpose.AUTH,
            is_used=False,
        ).update(
            is_used=True,
        )

        otp = OTPCode.objects.create(
            phone_number=phone_number,
            code_hash=hash_otp(
                otp_code
            ),
            purpose=OTPCode.OTPPurpose.AUTH,
            expires_at=expires_at,
            max_attempts=(
                settings.AUTH_OTP_MAX_ATTEMPTS
            ),
        )

    try:
        delivery = send_auth_otp_sms(
            phone_number=phone_number,
            otp_code=otp_code,
        )

    except OTPDeliveryError as exc:
        OTPCode.objects.filter(
            pk=otp.pk
        ).update(
            is_used=True
        )

        raise OTPDeliveryServiceError(
            "ارسال کد تایید ناموفق بود."
        ) from exc

    except Exception as exc:
        OTPCode.objects.filter(
            pk=otp.pk
        ).update(
            is_used=True
        )

        raise OTPDeliveryServiceError(
            "سرویس ارسال کد تایید در دسترس نیست."
        ) from exc

    return {
        "expires_in": (
            settings.AUTH_OTP_EXPIRE_SECONDS
        ),
        "debug_otp": delivery.get(
            "debug_otp"
        ),
    }



def verify_auth_otp(
    *,
    phone_number,
    otp_code,
):
    pending_error = None
    result = None

    with transaction.atomic():
        otp = (
            OTPCode.objects
            .select_for_update()
            .filter(
                phone_number=phone_number,
                purpose=OTPCode.OTPPurpose.AUTH,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            raise InvalidOTPError(
                "کد تایید معتبر نیست."
            )

        if otp.is_expired:
            otp.is_used = True

            otp.save(
                update_fields=[
                    "is_used",
                ]
            )

            pending_error = ExpiredOTPError(
                "کد تایید منقضی شده است."
            )

        elif otp.attempts >= otp.max_attempts:
            otp.is_used = True

            otp.save(
                update_fields=[
                    "is_used",
                ]
            )

            pending_error = OTPAttemptsExceededError(
                "تعداد تلاش‌های مجاز به پایان رسیده است."
            )

        elif not verify_otp_hash(
            otp_code,
            otp.code_hash,
        ):
            otp.attempts += 1

            update_fields = [
                "attempts",
            ]

            if otp.attempts >= otp.max_attempts:
                otp.is_used = True

                update_fields.append(
                    "is_used"
                )

            otp.save(
                update_fields=update_fields
            )

            remaining_attempts = max(
                0,
                otp.max_attempts
                - otp.attempts,
            )

            pending_error = OTPCodeMismatchError(
                "کد تایید اشتباه است.",
                extra={
                    "remaining_attempts": (
                        remaining_attempts
                    ),
                },
            )

        else:
            otp.is_used = True

            otp.save(
                update_fields=[
                    "is_used",
                ]
            )

            try:
                user = (
                    User.objects
                    .select_for_update()
                    .get(
                        phone_number=phone_number
                    )
                )

                is_new_user = False

            except User.DoesNotExist:
                user = User.objects.create_user(
                    phone_number=phone_number,
                    is_phone_verified=True,
                )

                is_new_user = True

            if not user.is_active:
                pending_error = InactiveUserError(
                    "حساب کاربری غیرفعال است."
                )

            else:
                update_fields = []

                if not user.is_phone_verified:
                    user.is_phone_verified = True

                    update_fields.append(
                        "is_phone_verified"
                    )

                if update_fields:
                    user.save(
                        update_fields=update_fields
                    )

                result = {
                    "user": user,
                    "is_new_user": is_new_user,
                }

    # مهم:
    # Exception بعد از پایان transaction
    # ایجاد می‌شود تا تغییرات OTP rollback نشوند.
    if pending_error is not None:
        raise pending_error

    return result


def get_next_page(user):
    if user.is_profile_completed:
        return "home"

    return "complete_profile"
