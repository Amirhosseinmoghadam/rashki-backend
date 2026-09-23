from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager
from accounts.validators import validate_iran_mobile


class User(AbstractBaseUser, PermissionsMixin):
    """
    کاربر اصلی سیستم.

    Login identifier:
        phone_number

    Customer authentication:
        Phone Number + OTP
    """

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=11,
        unique=True,
        validators=[validate_iran_mobile],
        error_messages={
            "unique": (
                "کاربری با این شماره موبایل "
                "قبلاً ثبت شده است."
            ),
        },
    )

    first_name = models.CharField(
        _("First Name"),
        max_length=100,
        blank=True,
    )

    last_name = models.CharField(
        _("Last Name"),
        max_length=100,
        blank=True,
    )

    is_phone_verified = models.BooleanField(
        _("Phone Verified"),
        default=False,
    )

    is_active = models.BooleanField(
        _("Active"),
        default=True,
    )

    is_staff = models.BooleanField(
        _("Staff Status"),
        default=False,
        help_text=_(
            "Designates whether the user "
            "can log into the admin site."
        ),
    )

    date_joined = models.DateTimeField(
        _("Date Joined"),
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("Updated At"),
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()

    def get_short_name(self):
        return self.first_name or self.phone_number

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def is_profile_completed(self):
        return bool(
            self.first_name.strip()
            and self.last_name.strip()
        )


class OTPCode(models.Model):
    """
    OTP خام هرگز ذخیره نمی‌شود.
    فقط HMAC hash داخل دیتابیس قرار می‌گیرد.
    """

    class OTPPurpose(models.TextChoices):
        AUTH = "auth", _("Authentication")

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=11,
        db_index=True,
        validators=[validate_iran_mobile],
    )

    code_hash = models.CharField(
        _("Code Hash"),
        max_length=128,
    )

    purpose = models.CharField(
        _("Purpose"),
        max_length=20,
        choices=OTPPurpose.choices,
        default=OTPPurpose.AUTH,
    )

    attempts = models.PositiveSmallIntegerField(
        _("Attempts"),
        default=0,
    )

    max_attempts = models.PositiveSmallIntegerField(
        _("Max Attempts"),
        default=5,
    )

    is_used = models.BooleanField(
        _("Used"),
        default=False,
    )

    expires_at = models.DateTimeField(
        _("Expires At"),
    )

    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("OTP Code")
        verbose_name_plural = _("OTP Codes")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=[
                    "phone_number",
                    "purpose",
                    "is_used",
                    "-created_at",
                ],
                name="otp_phone_purp_used_idx",
            ),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.purpose}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self):
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < self.max_attempts
        )
