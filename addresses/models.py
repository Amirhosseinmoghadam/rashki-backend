from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class Province(models.Model):
    """استان داخلی سیستم."""

    name = models.CharField(
        _("Name"),
        max_length=100,
        unique=True,
        help_text=_("The official name of the province."),
    )

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    """شهر داخلی سیستم."""

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name=_("Province"),
        help_text=_("The province this city belongs to."),
    )

    name = models.CharField(
        _("Name"),
        max_length=150,
        help_text=_("The official name of the city."),
    )

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["province__name", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["province", "name"],
                name="unique_city_name_per_province",
            ),
        ]

        indexes = [
            models.Index(
                fields=["province", "name"],
                name="address_city_prov_name_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.province.name})"


class Address(models.Model):
    """آدرس گیرنده متعلق به یک User."""

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
            ),
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
            ),
        ],
        null=True,
        blank=True,
        verbose_name="شماره تلفن ثابت",
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="addresses",
        verbose_name="استان",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="addresses",
        verbose_name="شهر",
    )

    postal_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{10}$",
                message="کد پستی باید 10 رقم باشد.",
            ),
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
        ordering = ["-is_default", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="unique_default_address_per_user",
            ),
        ]

        indexes = [
            models.Index(
                fields=["user", "is_default"],
                name="address_user_default_idx",
            ),
        ]

    def __str__(self):
        full_name = (
            f"{self.first_name or ''} "
            f"{self.last_name or ''}"
        ).strip()

        city_name = self.city.name if self.city_id else "-"

        return f"{full_name or '-'} - {city_name}"
