from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class Province(models.Model):
    """
    Model representing a Province in Iran.
    """

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
        """String representation of the Province object."""
        return self.name


class City(models.Model):
    """
    Model representing a City in Iran, belonging to a Province.
    """

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
        # Ensures that the combination of province and city name is unique.
        unique_together = ("province", "name")
        ordering = ["province__name", "name"]

    def __str__(self):
        """String representation of the City object."""
        return f"{self.name} ({self.province.name})"


class Location(models.Model):
    """
    Model representing a geographical location (Province and City).
    """

    province = models.ForeignKey(
        "addresses.Province", on_delete=models.CASCADE, verbose_name="Province"
    )
    city = models.ForeignKey(
        "addresses.City",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="City",
    )

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.province.name}, {self.city.name if self.city else 'N/A'}"


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
        "addresses.Province",
        on_delete=models.PROTECT,
        verbose_name="استان",
    )

    city = models.ForeignKey(
        "addresses.City",
        on_delete=models.PROTECT,
        verbose_name="شهر",
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