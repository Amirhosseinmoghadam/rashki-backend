from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
)
from rest_framework_simplejwt.settings import (
    api_settings,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from accounts.models import (
    OTPCode,
)

from accounts.otp import (
    check_send_otp_rate_limit,
    check_verify_otp_rate_limit,
    generate_otp,
    hash_otp,
)

from accounts.services import (
    AccountServiceError,
    create_tokens,
    get_next_page,
    get_user_data,
    verify_auth_otp,
)

from .openapi.schema import (
    complete_profile_view_schema,
    me_get_view_schema,
    me_update_view_schema,
    otp_verify_view_schema,
    send_otp_view_schema,
    token_refresh_view_schema,
    user_logout_api_view_schema,
)

from .serializers import (
    CompleteProfileSerializer,
    LogoutSerializer,
    OTPVerifySerializer,
    SendOTPSerializer,
    UserSerializer,
)


# =========================================================
# Response Helpers
# =========================================================


def success_response(
    *,
    message,
    data=None,
    http_status=status.HTTP_200_OK,
):
    return Response(
        {
            "success": True,
            "message": message,
            "data": data,
        },
        status=http_status,
    )


def error_response(
    *,
    message,
    errors=None,
    http_status=status.HTTP_400_BAD_REQUEST,
):
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status=http_status,
    )


# =========================================================
# Send OTP
# =========================================================


class SendOTPView(APIView):
    """
    ارسال OTP برای Login / Signup.

    در حال حاضر OTP داخل Console چاپ می‌شود.

    بعداً SMS Provider واقعی به این View
    متصل خواهد شد.
    """

    permission_classes = [
        AllowAny,
    ]

    @send_otp_view_schema
    def post(
        self,
        request,
    ):
        # -------------------------------------------------
        # Serializer
        # -------------------------------------------------

        serializer = SendOTPSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            return error_response(
                message=(
                    "اطلاعات ارسالی معتبر نیست."
                ),
                errors=serializer.errors,
            )

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        # -------------------------------------------------
        # Rate Limit
        # -------------------------------------------------

        rate_limit = (
            check_send_otp_rate_limit(
                request,
                phone_number,
            )
        )

        if not rate_limit[
            "allowed"
        ]:
            return error_response(
                message=(
                    "تعداد درخواست‌ها "
                    "بیش از حد مجاز است."
                ),
                errors={
                    "retry_after": (
                        rate_limit[
                            "retry_after"
                        ]
                    ),
                    "reason": (
                        rate_limit.get(
                            "reason"
                        )
                    ),
                },
                http_status=(
                    status
                    .HTTP_429_TOO_MANY_REQUESTS
                ),
            )

        # -------------------------------------------------
        # Generate OTP
        # -------------------------------------------------

        otp_code = generate_otp()

        # -------------------------------------------------
        # Development Debug
        # -------------------------------------------------

        print(
            "otp_code:",
            otp_code,
        )

        # -------------------------------------------------
        # Hash OTP
        # -------------------------------------------------

        otp_hash = hash_otp(
            otp_code
        )

        # -------------------------------------------------
        # Expiration
        # -------------------------------------------------

        expires_at = (
            timezone.now()
            + timedelta(
                seconds=(
                    settings
                    .AUTH_OTP_EXPIRE_SECONDS
                )
            )
        )

        # -------------------------------------------------
        # Database
        # -------------------------------------------------

        with transaction.atomic():

            # ---------------------------------------------
            # Invalidate previous active OTPs
            # ---------------------------------------------

            (
                OTPCode.objects
                .filter(
                    phone_number=(
                        phone_number
                    ),
                    purpose=(
                        OTPCode
                        .OTPPurpose
                        .AUTH
                    ),
                    is_used=False,
                )
                .update(
                    is_used=True,
                )
            )

            # ---------------------------------------------
            # Create OTP
            # ---------------------------------------------

            OTPCode.objects.create(
                phone_number=(
                    phone_number
                ),

                code_hash=(
                    otp_hash
                ),

                purpose=(
                    OTPCode
                    .OTPPurpose
                    .AUTH
                ),

                expires_at=(
                    expires_at
                ),

                max_attempts=(
                    settings
                    .AUTH_OTP_MAX_ATTEMPTS
                ),
            )

        # -------------------------------------------------
        # SMS Provider
        # -------------------------------------------------

        # send_sms(
        #     phone_number=phone_number,
        #     code=otp_code,
        # )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return success_response(
            message=(
                "کد تایید با موفقیت ارسال شد."
            ),
            data={
                "expires_in": (
                    settings
                    .AUTH_OTP_EXPIRE_SECONDS
                ),
            },
        )


# =========================================================
# Verify OTP
# =========================================================


class OTPVerifyView(APIView):
    """
    Login + Signup یکپارچه.

    Existing User:
        Login

    New User:
        Create User
        Login
    """

    permission_classes = [
        AllowAny,
    ]

    @otp_verify_view_schema
    def post(
        self,
        request,
    ):
        # -------------------------------------------------
        # Serializer
        # -------------------------------------------------

        serializer = OTPVerifySerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            return error_response(
                message=(
                    "اطلاعات ارسالی معتبر نیست."
                ),
                errors=serializer.errors,
            )

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        otp_code = (
            serializer.validated_data[
                "otp_code"
            ]
        )

        # -------------------------------------------------
        # Rate Limit
        # -------------------------------------------------

        rate_limit = (
            check_verify_otp_rate_limit(
                request,
                phone_number,
            )
        )

        if not rate_limit[
            "allowed"
        ]:
            return error_response(
                message=(
                    "تعداد تلاش‌های تایید "
                    "بیش از حد مجاز است."
                ),
                errors={
                    "retry_after": (
                        rate_limit[
                            "retry_after"
                        ]
                    ),
                    "reason": (
                        rate_limit.get(
                            "reason"
                        )
                    ),
                },
                http_status=(
                    status
                    .HTTP_429_TOO_MANY_REQUESTS
                ),
            )

        # -------------------------------------------------
        # Verify OTP
        # -------------------------------------------------

        try:
            result = verify_auth_otp(
                phone_number=(
                    phone_number
                ),
                otp_code=(
                    otp_code
                ),
            )

        except AccountServiceError as exc:
            return error_response(
                message=(
                    exc.message
                ),
                errors={
                    "code": (
                        exc.error_code
                    ),
                    **exc.extra,
                },
                http_status=(
                    exc.status_code
                ),
            )

        # -------------------------------------------------
        # User
        # -------------------------------------------------

        user = result[
            "user"
        ]

        # -------------------------------------------------
        # JWT
        # -------------------------------------------------

        tokens = create_tokens(
            user
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return success_response(
            message=(
                "احراز هویت با "
                "موفقیت انجام شد."
            ),
            data={
                "is_new_user": (
                    result[
                        "is_new_user"
                    ]
                ),

                "is_profile_completed": (
                    user
                    .is_profile_completed
                ),

                "next": (
                    get_next_page(
                        user
                    )
                ),

                "user": (
                    get_user_data(
                        user
                    )
                ),

                "tokens": (
                    tokens
                ),
            },
        )


# =========================================================
# Complete Profile
# =========================================================


class CompleteProfileView(APIView):
    """
    تکمیل اولیه پروفایل.

    این Endpoint برای Onboarding است
    و نام و نام خانوادگی هر دو لازم هستند.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @complete_profile_view_schema
    def patch(
        self,
        request,
    ):
        serializer = (
            CompleteProfileSerializer(
                request.user,
                data=request.data,
                partial=False,
            )
        )

        if not serializer.is_valid():
            return error_response(
                message=(
                    "اطلاعات ارسالی معتبر نیست."
                ),
                errors=serializer.errors,
            )

        user = serializer.save()

        return success_response(
            message=(
                "اطلاعات کاربر "
                "با موفقیت تکمیل شد."
            ),
            data={
                "is_profile_completed": (
                    user
                    .is_profile_completed
                ),

                "next": (
                    get_next_page(
                        user
                    )
                ),

                "user": (
                    get_user_data(
                        user
                    )
                ),
            },
        )


# =========================================================
# Current User
# =========================================================


class UserMeAPIView(APIView):
    """
    دریافت و ویرایش اطلاعات کاربر فعلی.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    @me_get_view_schema
    def get(
        self,
        request,
    ):
        return success_response(
            message=(
                "اطلاعات کاربر "
                "با موفقیت دریافت شد."
            ),
            data=(
                UserSerializer(
                    request.user
                ).data
            ),
        )

    # -----------------------------------------------------
    # PATCH
    # -----------------------------------------------------

    @me_update_view_schema
    def patch(
        self,
        request,
    ):
        serializer = (
            CompleteProfileSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
        )

        if not serializer.is_valid():
            return error_response(
                message=(
                    "اطلاعات ارسالی معتبر نیست."
                ),
                errors=serializer.errors,
            )

        user = serializer.save()

        return success_response(
            message=(
                "اطلاعات کاربر "
                "با موفقیت بروزرسانی شد."
            ),
            data=(
                UserSerializer(
                    user
                ).data
            ),
        )


# =========================================================
# JWT Refresh
# =========================================================


class AccountTokenRefreshView(
    TokenRefreshView
):
    """
    Refresh JWT Access Token.
    """

    permission_classes = [
        AllowAny,
    ]

    @token_refresh_view_schema
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        serializer = (
            self.get_serializer(
                data=request.data
            )
        )

        try:
            serializer.is_valid(
                raise_exception=True
            )

        except (
            InvalidToken,
            TokenError,
        ):
            return error_response(
                message=(
                    "Refresh token نامعتبر "
                    "یا منقضی شده است."
                ),
                errors={
                    "code": (
                        "invalid_refresh_token"
                    )
                },
                http_status=(
                    status
                    .HTTP_401_UNAUTHORIZED
                ),
            )

        return success_response(
            message=(
                "Access token با موفقیت "
                "بروزرسانی شد."
            ),
            data=(
                serializer.validated_data
            ),
        )


# =========================================================
# Logout
# =========================================================


class UserLogoutAPIView(APIView):
    """
    خروج از حساب.

    Refresh Token باید متعلق به
    همان User احراز هویت‌شده باشد.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @user_logout_api_view_schema
    def post(
        self,
        request,
    ):
        # -------------------------------------------------
        # Serializer
        # -------------------------------------------------

        context = {}

        serializer = LogoutSerializer(
            data=request.data,
            context=context,
        )

        if not serializer.is_valid():
            return error_response(
                message=(
                    "Refresh token معتبر نیست."
                ),
                errors=serializer.errors,
            )

        # -------------------------------------------------
        # Validated Token
        # -------------------------------------------------

        token = context.get(
            "validated_token"
        )

        # -------------------------------------------------
        # Token User ID
        # -------------------------------------------------

        token_user_id = token.get(
            api_settings.USER_ID_CLAIM
        )

        current_user_id = getattr(
            request.user,
            api_settings.USER_ID_FIELD,
        )

        # -------------------------------------------------
        # Ownership Check
        # -------------------------------------------------

        if (
            str(token_user_id)
            != str(current_user_id)
        ):
            return error_response(
                message=(
                    "Refresh token متعلق "
                    "به این کاربر نیست."
                ),
                errors={
                    "code": (
                        "token_owner_mismatch"
                    )
                },
                http_status=(
                    status
                    .HTTP_403_FORBIDDEN
                ),
            )

        # -------------------------------------------------
        # Blacklist
        # -------------------------------------------------

        try:
            token.blacklist()

        except TokenError:
            return error_response(
                message=(
                    "Refresh token نامعتبر "
                    "یا قبلاً غیرفعال شده است."
                ),
                errors={
                    "code": (
                        "invalid_refresh_token"
                    )
                },
                http_status=(
                    status
                    .HTTP_401_UNAUTHORIZED
                ),
            )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return success_response(
            message=(
                "خروج از حساب "
                "با موفقیت انجام شد."
            ),
            data=None,
        )