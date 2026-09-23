import re

from django.conf import settings

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.validators import normalize_phone_number


PHONE_REGEX = re.compile(
    settings.AUTH_PHONE_REGEX_PATTERN
)

OTP_LENGTH = settings.AUTH_OTP_LENGTH


class UserSerializer(serializers.ModelSerializer):
    is_profile_completed = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "is_phone_verified",
            "is_profile_completed",
        ]

        read_only_fields = [
            "id",
            "phone_number",
            "is_phone_verified",
            "is_profile_completed",
        ]


class BasePhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        required=True,
        trim_whitespace=True,
        error_messages={
            "required": (
                "وارد کردن شماره تلفن الزامی است."
            ),
            "blank": (
                "شماره تلفن نمی‌تواند خالی باشد."
            ),
            "min_length": (
                "شماره تلفن باید دقیقاً ۱۱ رقم باشد."
            ),
            "max_length": (
                "شماره تلفن باید دقیقاً ۱۱ رقم باشد."
            ),
        },
    )

    def validate_phone_number(
        self,
        value,
    ):
        value = normalize_phone_number(
            value
        )

        if not PHONE_REGEX.fullmatch(value):
            raise serializers.ValidationError(
                (
                    "شماره تلفن همراه باید با 09 "
                    "شروع شود و ۱۱ رقم باشد."
                )
            )

        return value


class SendOTPSerializer(BasePhoneSerializer):
    pass


class OTPVerifySerializer(BasePhoneSerializer):
    otp_code = serializers.CharField(
        max_length=OTP_LENGTH,
        min_length=OTP_LENGTH,
        required=True,
        trim_whitespace=True,
        error_messages={
            "required": (
                "وارد کردن کد تایید الزامی است."
            ),
            "blank": (
                "کد تایید نمی‌تواند خالی باشد."
            ),
            "min_length": (
                f"کد تایید باید دقیقاً "
                f"{OTP_LENGTH} رقم باشد."
            ),
            "max_length": (
                f"کد تایید باید دقیقاً "
                f"{OTP_LENGTH} رقم باشد."
            ),
        },
    )

    def validate_otp_code(
        self,
        value,
    ):
        if not value.isdigit():
            raise serializers.ValidationError(
                "کد تایید باید فقط شامل ارقام باشد."
            )

        return value


class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]

        extra_kwargs = {
            "first_name": {
                "required": True,
                "allow_blank": False,
            },
            "last_name": {
                "required": True,
                "allow_blank": False,
            },
        }

    def validate_first_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام الزامی است."
            )

        return value

    def validate_last_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام خانوادگی الزامی است."
            )

        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    def validate_refresh(
        self,
        value,
    ):
        try:
            token = RefreshToken(value)
        except Exception as exc:
            raise serializers.ValidationError(
                (
                    "Refresh token نامعتبر است "
                    "یا قبلاً غیرفعال شده است."
                )
            ) from exc

        self.context[
            "validated_token"
        ] = token

        return value
