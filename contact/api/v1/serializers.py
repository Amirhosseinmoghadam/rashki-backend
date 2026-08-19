import re

from django.utils import timezone
from datetime import timedelta

from rest_framework import serializers

from contact.models import ContactRequest


def normalize_digits(value: str) -> str:
    """
    تبدیل اعداد فارسی و عربی به انگلیسی.
    """

    translation_table = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789",
    )

    return value.translate(translation_table)


def normalize_text(value: str) -> str:
    """
    پاکسازی ساده متن بدون اجرای HTML یا تغییر محتوای واقعی.
    """

    value = value.strip()

    # حذف فاصله‌های پشت سر هم
    value = re.sub(r"\s+", " ", value)

    return value


class ContactRequestCreateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ContactRequest

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "subject",
            "description",
        ]

        extra_kwargs = {
            "first_name": {
                "max_length": 100,
            },
            "last_name": {
                "max_length": 100,
            },
            "phone_number": {
                "max_length": 11,
            },
            "description": {
                "max_length": 3000,
            },
        }

    def validate_first_name(self, value):
        value = normalize_text(value)

        if not value:
            raise serializers.ValidationError(
                "وارد کردن نام الزامی است."
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                "نام وارد شده معتبر نیست."
            )

        return value

    def validate_last_name(self, value):
        value = normalize_text(value)

        if not value:
            raise serializers.ValidationError(
                "وارد کردن نام خانوادگی الزامی است."
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                "نام خانوادگی وارد شده معتبر نیست."
            )

        return value

    def validate_phone_number(self, value):
        value = normalize_digits(value.strip())

        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError(
                "شماره تماس باید به صورت 09123456789 باشد."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "وارد کردن توضیحات الزامی است."
            )

        if len(value) < 5:
            raise serializers.ValidationError(
                "توضیحات باید حداقل ۵ کاراکتر باشد."
            )

        if len(value) > 3000:
            raise serializers.ValidationError(
                "توضیحات نمی‌تواند بیشتر از ۳۰۰۰ کاراکتر باشد."
            )

        return value

    def validate(self, attrs):
        """
        جلوگیری از ارسال چندباره یک درخواست مشابه
        توسط یک شماره تلفن در مدت کوتاه.
        """

        phone_number = attrs.get("phone_number")
        subject = attrs.get("subject")
        description = attrs.get("description")

        if not phone_number or not subject or not description:
            return attrs

        recent_time = timezone.now() - timedelta(minutes=5)

        duplicate_exists = ContactRequest.objects.filter(
            phone_number=phone_number,
            subject=subject,
            description=description,
            created_at__gte=recent_time,
        ).exists()

        if duplicate_exists:
            raise serializers.ValidationError(
                "این درخواست قبلاً ثبت شده است. "
                "لطفاً چند دقیقه بعد دوباره تلاش کنید."
            )

        return attrs


class ContactRequestAdminSerializer(
    serializers.ModelSerializer
):
    subject_display = serializers.CharField(
        source="get_subject_display",
        read_only=True,
    )

    class Meta:
        model = ContactRequest

        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "subject",
            "subject_display",
            "description",
            "is_read",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "subject",
            "subject_display",
            "description",
            "created_at",
            "updated_at",
        ]