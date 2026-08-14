from django.db import models
from django.utils.translation import gettext_lazy as _


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
        "base.Province", on_delete=models.CASCADE, verbose_name="Province"
    )
    city = models.ForeignKey(
        "base.City",
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
