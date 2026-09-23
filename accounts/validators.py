import re

from django.core.exceptions import ValidationError


IRAN_MOBILE_PATTERN = re.compile(r"^09\d{9}$")


def normalize_phone_number(value):
    return str(value or "").strip()


def validate_iran_mobile(value):
    value = normalize_phone_number(value)

    if not IRAN_MOBILE_PATTERN.fullmatch(value):
        raise ValidationError("شماره موبایل نامعتبر است.")

    return value
