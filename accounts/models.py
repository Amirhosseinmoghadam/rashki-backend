from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

# =========================================================
# User
# =========================================================


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.

    Authentication:
        Phone Number + OTP

    Username:
        phone_number
    """

    phone_validator = RegexValidator(
        regex=r"^09\d{9}$",
        message="شماره موبایل نامعتبر است.",
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=11,
        unique=True,
        db_index=True,
        validators=[phone_validator],
        editable=False,
        error_messages={
            "unique": ("کاربری با این شماره موبایل " "قبلاً ثبت شده است."),
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
        help_text=_("Designates whether the user can log into " "the admin site."),
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
        return (f"{self.first_name} {self.last_name}").strip()

    def get_short_name(self):
        return self.first_name or self.phone_number

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def is_profile_completed(self):
        """
        Basic profile completion.

        Currently:
            first_name
            last_name

        Address can be added later.
        """

        return bool(self.first_name.strip() and self.last_name.strip())


# =========================================================
# OTP
# =========================================================


class OTPCode(models.Model):
    """
    OTP verification model.

    The actual OTP is NEVER stored.
    Only an HMAC hash is stored.
    """

    class OTPPurpose(models.TextChoices):
        AUTH = "auth", _("Authentication")

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=11,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^09\d{9}$",
                message="شماره موبایل نامعتبر است.",
            )
        ],
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
                    "is_used",
                    "-created_at",
                ],
                name="otp_phone_used_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.phone_number} - " f"{self.purpose}"

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


# =========================================================
# Address
# =========================================================


class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("User"),
    )

    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="نام",
    )

    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="نام خانوادگی",
    )

    mobile_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^09[0-9]{9}$",
                message="شماره موبایل نامعتبر است.",
            )
        ],
        null=True,
        blank=True,
        verbose_name="شماره موبایل",
    )

    phone_number = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{11}$",
                message="شماره تلفن باید 11 رقم باشد.",
            )
        ],
        null=True,
        blank=True,
        verbose_name="شماره تلفن ثابت",
    )

    province = models.ForeignKey(
        "base.Province",
        on_delete=models.PROTECT,
        verbose_name="استان",
    )

    city = models.ForeignKey(
        "base.City",
        on_delete=models.PROTECT,
        verbose_name="شهر",
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="ایمیل",
    )

    postal_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{10}$",
                message="کد پستی باید 10 رقم باشد.",
            )
        ],
        null=True,
        blank=True,
        verbose_name="کد پستی",
    )

    postal_address = models.TextField(
        null=True,
        blank=True,
        verbose_name="آدرس پستی",
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="آدرس پیش‌فرض",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name=("unique_default_address_per_user"),
            )
        ]

    def set_as_default(self):
        Address.objects.filter(
            user=self.user,
            is_default=True,
        ).exclude(
            pk=self.pk
        ).update(is_default=False)

        self.is_default = True

        self.save(update_fields=["is_default"])

    def __str__(self):
        city_name = self.city.name if self.city_id else "-"

        return (
            f"{self.first_name or ''} " f"{self.last_name or ''} - " f"{city_name}"
        ).strip()
