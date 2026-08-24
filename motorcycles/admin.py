from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import MotorcycleBrand, MotorcycleModel


# =========================================================
# Motorcycle Model Inline
# =========================================================

class MotorcycleModelInline(admin.TabularInline):
    model = MotorcycleModel
    extra = 0
    fields = (
        "name",
        "slug",
        "production_start_year",
        "production_end_year",
        "engine_volume",
        "is_active",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }


# =========================================================
# Motorcycle Brand Admin
# =========================================================

@admin.register(MotorcycleBrand)
class MotorcycleBrandAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = (
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )

    list_per_page = 25

    inlines = (
        MotorcycleModelInline,
    )


# =========================================================
# Motorcycle Model Admin
# =========================================================

@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand",
        "production_start_year",
        "production_end_year",
        "engine_volume",
        "is_active",
        "created_at",
    )

    list_filter = (
        "brand",
        "is_active",
        "production_start_year",
        "production_end_year",
    )

    search_fields = (
        "name",
        "slug",
        "brand__name",
    )

    autocomplete_fields = (
        "brand",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    ordering = (
        "brand__name",
        "name",
    )

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "brand",
                    "name",
                    "slug",
                )
            },
        ),
        (
            "مشخصات موتور",
            {
                "fields": (
                    "production_start_year",
                    "production_end_year",
                    "engine_volume",
                    "description",
                    "image",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )