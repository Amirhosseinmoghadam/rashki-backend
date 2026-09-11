from django.contrib import admin
from django.utils.html import format_html

from .models import (
    MotorcycleBrand,
    MotorcycleModel,
)


# =========================================================
# Motorcycle Brand Admin
# =========================================================


@admin.register(MotorcycleBrand)
class MotorcycleBrandAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "name",
        "slug",
        "logo_preview",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "name",
    )

    list_per_page = 50

    readonly_fields = (
        "slug",
        "logo_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                ),
            },
        ),
        (
            "لوگو و وضعیت",
            {
                "fields": (
                    "logo",
                    "logo_preview",
                    "is_active",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
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

    @admin.display(
        description="پیش‌نمایش لوگو",
    )
    def logo_preview(
        self,
        obj,
    ):

        if not obj.logo:
            return "بدون لوگو"

        return format_html(
            '<img src="{}" '
            'width="80" '
            'height="80" '
            'style="'
            'object-fit:contain;'
            'border-radius:8px;'
            '" />',
            obj.logo.url,
        )


# =========================================================
# Motorcycle Model Admin
# =========================================================


@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "brand",
        "name",
        "engine_volume",
        "production_years",
        "image_preview",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "is_active",
        "brand",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "brand__name",
        "description",
    )

    ordering = (
        "brand__name",
        "name",
    )

    list_select_related = (
        "brand",
    )

    autocomplete_fields = (
        "brand",
    )

    list_per_page = 50

    readonly_fields = (
        "slug",
        "image_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "brand",
                    "name",
                    "slug",
                    "description",
                ),
            },
        ),
        (
            "مشخصات موتورسیکلت",
            {
                "fields": (
                    "engine_volume",
                    "production_start_year",
                    "production_end_year",
                ),
            },
        ),
        (
            "تصویر و وضعیت",
            {
                "fields": (
                    "image",
                    "image_preview",
                    "is_active",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
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

    @admin.display(
        description="سال تولید",
    )
    def production_years(
        self,
        obj,
    ):

        start = (
            obj.production_start_year
        )

        end = (
            obj.production_end_year
        )

        if start and end:
            return f"{start} - {end}"

        if start:
            return f"{start} - اکنون"

        if end:
            return f"تا {end}"

        return "-"

    @admin.display(
        description="پیش‌نمایش تصویر",
    )
    def image_preview(
        self,
        obj,
    ):

        if not obj.image:
            return "بدون تصویر"

        return format_html(
            '<img src="{}" '
            'width="100" '
            'height="70" '
            'style="'
            'object-fit:cover;'
            'border-radius:8px;'
            '" />',
            obj.image.url,
        )