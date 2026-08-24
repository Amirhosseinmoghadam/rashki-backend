from django.contrib import admin
from django.utils.html import format_html

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "parent",
        "slug",
        "is_active",
        "image_preview",
        "created_at",
        "updated_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "parent__name",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "parent",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = (
        "name",
    )

    list_per_page = 50

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                    "parent",
                    "description",
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

    @admin.display(description="پیش‌نمایش تصویر")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" '
                'style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url,
            )

        return "بدون تصویر"