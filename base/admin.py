from django.contrib import admin

from base.models import Province, City


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin options for the Province model."""

    list_display = ("name", "id")
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin options for the City model."""

    list_display = ("name", "province", "id")
    search_fields = ("name", "province__name")
    list_filter = ("province",)
    ordering = ("province", "name")
