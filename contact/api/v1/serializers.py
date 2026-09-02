import re

from datetime import timedelta

from django.utils import timezone

from rest_framework import serializers

from contact.models import ContactRequest

from utils.normalizers import (
    normalize_digits,
    normalize_single_line_text,
)


# =========================================================
# Contact Request Create Serializer
# =========================================================


class ContactRequestCreateSerializer(
    serializers.ModelSerializer
):

    # Explicit field prevents the model RegexValidator
    # from running before digit normalization.
    phone_number = serializers.CharField(
        max_length=11,
        min_length=11,
        required=True,
        trim_whitespace=True,
        error_messages={
            "required": (
                "وارد کردن شماره تماس الزامی است."
            ),
            "blank": (
                "شماره تماس نمی‌تواند خالی باشد."
            ),
            "min_length": (
                "شماره تماس باید ۱۱ رقم باشد."
            ),
            "max_length": (
                "شماره تماس باید ۱۱ رقم باشد."
            ),
        },
    )

    subject = serializers.ChoiceField(
        choices=ContactRequest.Subject.choices,
        required=True,
        error_messages={
            "required": (
                "انتخاب موضوع درخواست الزامی است."
            ),
            "invalid_choice": (
                "موضوع درخواست انتخاب‌شده "
                "معتبر نیست."
            ),
        },
    )

    class Meta:

        model = ContactRequest

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "subject",
            "description",
        ]

    # =====================================================
    # First Name
    # =====================================================

    def validate_first_name(
        self,
        value,
    ):

        value = normalize_single_line_text(
            value
        )

        if not value:
            raise serializers.ValidationError(
                "وارد کردن نام الزامی است."
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                "نام وارد شده معتبر نیست."
            )

        return value

    # =====================================================
    # Last Name
    # =====================================================

    def validate_last_name(
        self,
        value,
    ):

        value = normalize_single_line_text(
            value
        )

        if not value:
            raise serializers.ValidationError(
                "وارد کردن نام خانوادگی "
                "الزامی است."
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                "نام خانوادگی وارد شده "
                "معتبر نیست."
            )

        return value

    # =====================================================
    # Phone Number
    # =====================================================

    def validate_phone_number(
        self,
        value,
    ):

        value = normalize_digits(
            value.strip()
        )

        if not re.fullmatch(
            r"09\d{9}",
            value,
        ):
            raise serializers.ValidationError(
                "شماره تماس باید به صورت "
                "09123456789 باشد."
            )

        return value

    # =====================================================
    # Description
    # =====================================================

    def validate_description(
        self,
        value,
    ):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "وارد کردن توضیحات الزامی است."
            )

        if len(value) < 5:
            raise serializers.ValidationError(
                "توضیحات باید حداقل "
                "۵ کاراکتر باشد."
            )

        return value

    # =====================================================
    # Duplicate Request
    # =====================================================

    def validate(
        self,
        attrs,
    ):
        """
        Prevent identical contact requests
        from the same phone number within
        a short period.
        """

        phone_number = attrs.get(
            "phone_number"
        )

        subject = attrs.get(
            "subject"
        )

        description = attrs.get(
            "description"
        )

        if not all(
            [
                phone_number,
                subject,
                description,
            ]
        ):
            return attrs

        recent_time = (
            timezone.now()
            - timedelta(
                minutes=5
            )
        )

        duplicate_exists = (
            ContactRequest.objects.filter(
                phone_number=phone_number,
                subject=subject,
                description=description,
                created_at__gte=recent_time,
            )
            .exists()
        )

        if duplicate_exists:
            raise serializers.ValidationError(
                "این درخواست قبلاً ثبت شده است. "
                "لطفاً چند دقیقه بعد دوباره "
                "تلاش کنید."
            )

        return attrs


# =========================================================
# Contact Request Admin Serializer
# =========================================================


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
            "is_read",
            "created_at",
            "updated_at",
        ]


# =========================================================
# Contact Request Status Serializer
# =========================================================


class ContactRequestStatusSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ContactRequest

        fields = [
            "is_read",
        ]