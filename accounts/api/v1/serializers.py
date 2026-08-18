import re

from django.conf import settings

from rest_framework import serializers

from accounts.models import User,Address

from django.db import transaction


# =========================================================
# Settings
# =========================================================

PHONE_REGEX_PATTERN = settings.AUTH_PHONE_REGEX_PATTERN

OTP_LENGTH = settings.AUTH_OTP_LENGTH

PHONE_REGEX = re.compile(PHONE_REGEX_PATTERN)


# =========================================================
# Base Phone Serializer
# =========================================================


class BasePhoneSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        required=True,
        trim_whitespace=True,
        error_messages={
            "required": ("وارد کردن شماره تلفن الزامی است."),
            "blank": ("شماره تلفن نمی‌تواند خالی باشد."),
            "min_length": ("شماره تلفن باید دقیقاً " "۱۱ رقم باشد."),
            "max_length": ("شماره تلفن باید دقیقاً " "۱۱ رقم باشد."),
        },
    )

    def validate_phone_number(self, value):

        value = str(value).strip()

        if not PHONE_REGEX.fullmatch(value):
            raise serializers.ValidationError(
                "شماره تلفن همراه باید با 09 شروع " "شود و ۱۱ رقم باشد."
            )

        return value


# =========================================================
# Send OTP
# =========================================================


class SendOTPSerializer(BasePhoneSerializer):
    """
    Unified authentication.

    There is no Login / Register distinction.
    """


# =========================================================
# Verify OTP
# =========================================================


class OTPVerifySerializer(BasePhoneSerializer):

    otp_code = serializers.CharField(
        max_length=OTP_LENGTH,
        min_length=OTP_LENGTH,
        required=True,
        trim_whitespace=True,
        error_messages={
            "required": ("وارد کردن کد تایید الزامی است."),
            "blank": ("کد تایید نمی‌تواند خالی باشد."),
            "min_length": (f"کد تایید باید دقیقاً " f"{OTP_LENGTH} رقم باشد."),
            "max_length": (f"کد تایید باید دقیقاً " f"{OTP_LENGTH} رقم باشد."),
        },
    )

    def validate_otp_code(self, value):

        if not value.isdigit():
            raise serializers.ValidationError("کد تایید باید فقط شامل ارقام باشد.")

        return value


# =========================================================
# Complete Profile
# =========================================================


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

    def validate_first_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError("نام الزامی است.")

        return value

    def validate_last_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError("نام خانوادگی الزامی است.")

        return value



class AddressSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(
        source="province.name",
        read_only=True,
    )

    city_name = serializers.CharField(
        source="city.name",
        read_only=True,
    )

    class Meta:
        model = Address

        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
            "province",
            "province_name",
            "city",
            "city_name",
            "email",
            "postal_code",
            "postal_address",
            "is_default",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "province_name",
            "city_name",
            "created_at",
            "updated_at",
        ]


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address

        fields = [
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
            "province",
            "city",
            "email",
            "postal_code",
            "postal_address",
            "is_default",
        ]

    def validate(self, attrs):
        province = attrs.get("province")
        city = attrs.get("city")

        if province and city:
            if city.province_id != province.id:
                raise serializers.ValidationError(
                    {
                        "city": (
                            "شهر انتخاب‌شده متعلق به "
                            "استان انتخاب‌شده نیست."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        addresses = (
            Address.objects
            .select_for_update()
            .filter(user=user)
        )

        has_addresses = addresses.exists()

        # اولین آدرس کاربر پیش‌فرض باشد
        if not has_addresses:
            validated_data["is_default"] = True

        if validated_data.get("is_default") is True:
            addresses.filter(
                is_default=True
            ).update(
                is_default=False
            )

        return Address.objects.create(
            user=user,
            **validated_data,
        )


class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address

        fields = [
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
            "province",
            "city",
            "email",
            "postal_code",
            "postal_address",
            "is_default",
        ]

    def validate(self, attrs):
        instance = self.instance

        province = attrs.get(
            "province",
            instance.province,
        )

        city = attrs.get(
            "city",
            instance.city,
        )

        if province and city:
            if city.province_id != province.id:
                raise serializers.ValidationError(
                    {
                        "city": (
                            "شهر انتخاب‌شده متعلق به "
                            "استان انتخاب‌شده نیست."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance.user

        # آدرس پیش‌فرض دیگری انتخاب شده
        if validated_data.get("is_default") is True:
            (
                Address.objects
                .select_for_update()
                .filter(
                    user=user,
                    is_default=True,
                )
                .exclude(
                    pk=instance.pk
                )
                .update(
                    is_default=False
                )
            )

        # اجازه نمی‌دهیم کاربر تنها آدرس پیش‌فرض
        # خودش را unset کند.
        if (
            validated_data.get("is_default") is False
            and instance.is_default
        ):
            raise serializers.ValidationError(
                {
                    "is_default": (
                        "نمی‌توانید آدرس پیش‌فرض را "
                        "بدون انتخاب آدرس جدید حذف کنید."
                    )
                }
            )

        return super().update(
            instance,
            validated_data,
        )