from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import (
    RefreshToken,
)
from rest_framework_simplejwt.exceptions import (
    TokenError,
)

from accounts.models import User, OTPCode , Address
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
    AddressCreateSerializer,
    AddressSerializer,
    AddressUpdateSerializer,
)

from accounts.api.v1.otp import (
    generate_otp,
    hash_otp,
    verify_otp_hash,
    check_send_otp_rate_limit,
    check_verify_otp_rate_limit,
)


from accounts.api.v1.openapi.schema import (
    address_list_view_schema,
    address_create_view_schema,
    address_detail_view_schema,
    address_update_view_schema,
    address_partial_update_view_schema,
    address_delete_view_schema,
    address_set_default_view_schema,
)


# =========================================================
# Helpers
# =========================================================


def create_tokens(user):
    """
    Create JWT access + refresh tokens.
    """

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
        "is_phone_verified": (user.is_phone_verified),
    }


# =========================================================
# Send OTP
# =========================================================
@send_otp_view_schema
class SendOTPView(APIView):
    """
    Unified authentication endpoint.

    It does NOT distinguish Login from Signup.

    Existing user:
        -> authenticate

    New user:
        -> create after OTP verification
    """

    permission_classes = [AllowAny]

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
                    "detail": ("تعداد درخواست‌ها " "بیش از حد مجاز است."),
                    "retry_after": (rate_limit["retry_after"]),
                },
                status=(status.HTTP_429_TOO_MANY_REQUESTS),
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
        print("otp_code : ", otp_code)
        otp_hash = hash_otp(otp_code)
        print("otp_hash : ", otp_hash)

        # -------------------------------------------------
        # Expiration
        # -------------------------------------------------

        expires_at = timezone.now() + timedelta(
            seconds=(settings.AUTH_OTP_EXPIRE_SECONDS)
        )

        # -------------------------------------------------
        # Create OTP
        # -------------------------------------------------

        OTPCode.objects.create(
            phone_number=phone_number,
            code_hash=otp_hash,
            purpose=(OTPCode.OTPPurpose.AUTH),
            expires_at=expires_at,
            max_attempts=(settings.AUTH_OTP_MAX_ATTEMPTS),
        )

        # -------------------------------------------------
        # SMS Provider
        # -------------------------------------------------
        #
        # send_sms(
        #     phone_number=phone_number,
        #     code=otp_code,
        # )
        #
        # IMPORTANT:
        # Never return otp_code in production.
        #
        # -------------------------------------------------

        return Response(
            {
                "message": ("کد تایید با موفقیت ارسال شد."),
                "expires_in": (settings.AUTH_OTP_EXPIRE_SECONDS),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Verify OTP
# =========================================================
@otp_verify_view_schema
class OTPVerifyView(APIView):
    """
    Unified Login + Signup.

    Existing User:
        -> Login

    New User:
        -> Create User
        -> Login

    Frontend should use `next`:

        home
        complete_profile
    """

    permission_classes = [AllowAny]

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
                    "detail": ("تعداد تلاش‌های تایید " "بیش از حد مجاز است."),
                    "retry_after": (rate_limit["retry_after"]),
                },
                status=(status.HTTP_429_TOO_MANY_REQUESTS),
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
                {"detail": ("کد تایید معتبر نیست.")},
                status=(status.HTTP_400_BAD_REQUEST),
            )

        # -------------------------------------------------
        # Expiration
        # -------------------------------------------------

        if otp.is_expired:

            otp.is_used = True

            otp.save(update_fields=["is_used"])

            return Response(
                {"detail": ("کد تایید منقضی شده است.")},
                status=(status.HTTP_400_BAD_REQUEST),
            )

        # -------------------------------------------------
        # Attempts
        # -------------------------------------------------

        if otp.attempts >= otp.max_attempts:

            otp.is_used = True

            otp.save(update_fields=["is_used"])

            return Response(
                {"detail": ("تعداد تلاش‌های مجاز " "به پایان رسیده است.")},
                status=(status.HTTP_429_TOO_MANY_REQUESTS),
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

            # ---------------------------------------------
            # Last attempt
            # ---------------------------------------------

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
                    "detail": ("کد تایید اشتباه است."),
                    "remaining_attempts": (remaining_attempts),
                },
                status=(status.HTTP_400_BAD_REQUEST),
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
                "message": ("احراز هویت با موفقیت انجام شد."),
                "is_new_user": (is_new_user),
                "is_profile_completed": (is_profile_completed),
                "next": next_page,
                "user": get_user_data(user),
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Complete Profile
# =========================================================
@complete_profile_view_schema
class CompleteProfileView(APIView):
    """
    Complete basic user profile.

    Phone number cannot be changed here.
    """

    permission_classes = [IsAuthenticated]

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
                "message": ("اطلاعات کاربر " "با موفقیت تکمیل شد."),
                "is_profile_completed": (user.is_profile_completed),
                "next": ("home" if user.is_profile_completed else "complete_profile"),
                "user": get_user_data(user),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Logout
# =========================================================
@user_logout_api_view_schema
class UserLogoutAPIView(APIView):
    """
    Logout authenticated user.

    The refresh token is blacklisted.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:

            return Response(
                {"detail": ("Refresh token is required.")},
                status=(status.HTTP_400_BAD_REQUEST),
            )

        try:

            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {"message": ("Logout successful.")},
                status=status.HTTP_200_OK,
            )

        except TokenError:

            return Response(
                {"detail": ("Refresh token is invalid " "or already blacklisted.")},
                status=(status.HTTP_401_UNAUTHORIZED),
            )

# =========================================================
# AddressListCreateAPIView
# =========================================================
class AddressListCreateAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self, user):
        return (
            Address.objects
            .filter(user=user)
            .select_related(
                "province",
                "city",
            )
            .order_by(
                "-is_default",
                "-created_at",
            )
        )

    @address_list_view_schema
    def get(self, request):
        addresses = self.get_queryset(
            request.user
        )

        serializer = AddressSerializer(
            addresses,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست آدرس‌ها با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_create_view_schema
    def post(self, request):
        serializer = AddressCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت ایجاد شد."
                ),
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# AddressDetailAPIView
# =========================================================
class AddressDetailAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, request, pk):
        return (
            Address.objects
            .filter(
                pk=pk,
                user=request.user,
            )
            .select_related(
                "province",
                "city",
            )
            .first()
        )

    @address_detail_view_schema
    def get(self, request, pk):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_update_view_schema
    @transaction.atomic
    def put(self, request, pk):
        return self._update(
            request,
            pk,
            partial=False,
        )

    @address_partial_update_view_schema
    @transaction.atomic
    def patch(self, request, pk):
        return self._update(
            request,
            pk,
            partial=True,
        )

    def _update(
        self,
        request,
        pk,
        partial=False,
    ):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AddressUpdateSerializer(
            address,
            data=request.data,
            partial=partial,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت بروزرسانی شد."
                ),
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_delete_view_schema
    @transaction.atomic
    def delete(self, request, pk):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        was_default = address.is_default

        address.delete()

        # اگر آدرس پیش‌فرض حذف شد،
        # یک آدرس دیگر را پیش‌فرض کن.
        if was_default:
            new_default = (
                Address.objects
                .filter(
                    user=request.user
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )

            if new_default:
                new_default.set_as_default()

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# AddressSetDefaultAPIView
# =========================================================
class AddressSetDefaultAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @address_set_default_view_schema
    @transaction.atomic
    def post(self, request, pk):
        address = (
            Address.objects
            .select_for_update()
            .filter(
                pk=pk,
                user=request.user,
            )
            .first()
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # همه آدرس‌های قبلی غیرپیش‌فرض شوند
        (
            Address.objects
            .filter(
                user=request.user,
                is_default=True,
            )
            .exclude(
                pk=address.pk
            )
            .update(
                is_default=False
            )
        )

        address.is_default = True

        address.save(
            update_fields=[
                "is_default",
                "updated_at",
            ]
        )

        serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس پیش‌فرض با موفقیت تغییر کرد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

