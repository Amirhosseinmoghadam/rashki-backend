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

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import User, OTPCode

from .openapi.schema import (
    send_otp_view_schema,
    otp_verify_view_schema,
    complete_profile_view_schema,
    user_logout_api_view_schema,
)

from .serializers import (
    SendOTPSerializer,
    OTPVerifySerializer,
    CompleteProfileSerializer,
)

from accounts.api.v1.otp import (
    generate_otp,
    hash_otp,
    verify_otp_hash,
    check_send_otp_rate_limit,
    check_verify_otp_rate_limit,
)

# =========================================================
# Helpers
# =========================================================


def create_tokens(user):
    """
    ایجاد JWT access و refresh token برای کاربر.
    """

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_user_data(user):
    """
    اطلاعات عمومی کاربر برای Response.
    """

    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_phone_verified": user.is_phone_verified,
    }


# =========================================================
# Send OTP
# =========================================================


class SendOTPView(APIView):
    """
    Unified authentication endpoint.

    Existing user:
        -> Authenticate

    New user:
        -> Create after OTP verification
    """

    permission_classes = [AllowAny]

    @send_otp_view_schema
    def post(self, request):

        serializer = SendOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # -------------------------------------------------
        # Rate Limit
        # -------------------------------------------------

        rate_limit = check_send_otp_rate_limit(
            request,
            phone_number,
        )

        if not rate_limit["allowed"]:
            return Response(
                {
                    "detail": "تعداد درخواست‌ها بیش از حد مجاز است.",
                    "retry_after": rate_limit["retry_after"],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # -------------------------------------------------
        # Invalidate previous active OTPs
        # -------------------------------------------------

        OTPCode.objects.filter(
            phone_number=phone_number,
            is_used=False,
        ).update(
            is_used=True,
        )

        # -------------------------------------------------
        # Generate OTP
        # -------------------------------------------------

        otp_code = generate_otp()

        # فقط برای Development
        print("otp_code:", otp_code)

        otp_hash = hash_otp(otp_code)

        # -------------------------------------------------
        # Expiration
        # -------------------------------------------------

        expires_at = timezone.now() + timedelta(
            seconds=settings.AUTH_OTP_EXPIRE_SECONDS
        )

        # -------------------------------------------------
        # Create OTP
        # -------------------------------------------------

        OTPCode.objects.create(
            phone_number=phone_number,
            code_hash=otp_hash,
            purpose=OTPCode.OTPPurpose.AUTH,
            expires_at=expires_at,
            max_attempts=settings.AUTH_OTP_MAX_ATTEMPTS,
        )

        # -------------------------------------------------
        # SMS Provider
        # -------------------------------------------------

        # send_sms(
        #     phone_number=phone_number,
        #     code=otp_code,
        # )

        return Response(
            {
                "message": "کد تایید با موفقیت ارسال شد.",
                "expires_in": settings.AUTH_OTP_EXPIRE_SECONDS,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Verify OTP
# =========================================================


class OTPVerifyView(APIView):
    """
    Unified Login + Signup.

    Existing User:
        -> Login

    New User:
        -> Create User
        -> Login
    """

    permission_classes = [AllowAny]

    @otp_verify_view_schema
    @transaction.atomic
    def post(self, request):

        serializer = OTPVerifySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]

        # -------------------------------------------------
        # Rate Limit
        # -------------------------------------------------

        rate_limit = check_verify_otp_rate_limit(
            request,
            phone_number,
        )

        if not rate_limit["allowed"]:
            return Response(
                {
                    "detail": "تعداد تلاش‌های تایید بیش از حد مجاز است.",
                    "retry_after": rate_limit["retry_after"],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # -------------------------------------------------
        # Get and lock latest OTP
        # -------------------------------------------------

        otp = (
            OTPCode.objects.select_for_update()
            .filter(
                phone_number=phone_number,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            return Response(
                {
                    "detail": "کد تایید معتبر نیست.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Expiration
        # -------------------------------------------------

        if otp.is_expired:

            otp.is_used = True

            otp.save(update_fields=["is_used"])

            return Response(
                {
                    "detail": "کد تایید منقضی شده است.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # Attempts
        # -------------------------------------------------

        if otp.attempts >= otp.max_attempts:

            otp.is_used = True

            otp.save(update_fields=["is_used"])

            return Response(
                {
                    "detail": "تعداد تلاش‌های مجاز به پایان رسیده است.",
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # -------------------------------------------------
        # Verify OTP
        # -------------------------------------------------

        is_valid_code = verify_otp_hash(
            otp_code,
            otp.code_hash,
        )

        if not is_valid_code:

            otp.attempts += 1

            update_fields = ["attempts"]

            if otp.attempts >= otp.max_attempts:

                otp.is_used = True

                update_fields.append("is_used")

            otp.save(update_fields=update_fields)

            remaining_attempts = max(
                0,
                otp.max_attempts - otp.attempts,
            )

            return Response(
                {
                    "detail": "کد تایید اشتباه است.",
                    "remaining_attempts": remaining_attempts,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -------------------------------------------------
        # OTP is valid
        # -------------------------------------------------

        otp.is_used = True

        otp.save(update_fields=["is_used"])

        # -------------------------------------------------
        # Find or Create User
        # -------------------------------------------------

        user, is_new_user = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                "is_phone_verified": True,
            },
        )

        # -------------------------------------------------
        # Existing user
        # -------------------------------------------------

        if not user.is_phone_verified:

            user.is_phone_verified = True

            user.save(update_fields=["is_phone_verified"])

        # -------------------------------------------------
        # Profile
        # -------------------------------------------------

        is_profile_completed = user.is_profile_completed

        # -------------------------------------------------
        # Navigation
        # -------------------------------------------------

        if is_profile_completed:
            next_page = "home"
        else:
            next_page = "complete_profile"

        # -------------------------------------------------
        # JWT
        # -------------------------------------------------

        tokens = create_tokens(user)

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return Response(
            {
                "message": "احراز هویت با موفقیت انجام شد.",
                "is_new_user": is_new_user,
                "is_profile_completed": is_profile_completed,
                "next": next_page,
                "user": get_user_data(user),
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Complete Profile
# =========================================================


class CompleteProfileView(APIView):
    """
    Complete basic user profile.

    Phone number cannot be changed here.
    """

    permission_classes = [IsAuthenticated]

    @complete_profile_view_schema
    def patch(self, request):

        serializer = CompleteProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                "message": "اطلاعات کاربر با موفقیت تکمیل شد.",
                "is_profile_completed": user.is_profile_completed,
                "next": ("home" if user.is_profile_completed else "complete_profile"),
                "user": get_user_data(user),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Logout
# =========================================================


class UserLogoutAPIView(APIView):
    """
    Logout authenticated user.

    The refresh token is blacklisted.
    """

    permission_classes = [IsAuthenticated]

    @user_logout_api_view_schema
    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "detail": "Refresh token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:

            return Response(
                {
                    "detail": ("Refresh token is invalid " "or already blacklisted."),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
