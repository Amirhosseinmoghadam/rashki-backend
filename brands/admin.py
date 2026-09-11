from django.contrib import admin
from django.utils.html import format_html

from .models import Brand


# =========================================================
# Brand Admin
# =========================================================


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

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
        "description",
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
                    "description",
                    "website",
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
            'style="object-fit:contain;'
            'border-radius:8px;" />',
            obj.logo.url,
        )