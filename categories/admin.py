from django.contrib import admin
from django.utils.html import format_html

from categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    # =====================================================
    # List
    # =====================================================

    list_display = (
        "id",
        "name",
        "parent_display",
        "slug",
        "is_active",
        "image_preview",
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
        "parent__name",
    )

    ordering = (
        "name",
    )

    list_per_page = 50

    list_select_related = (
        "parent",
    )

    # =====================================================
    # Relations
    # =====================================================

    autocomplete_fields = (
        "parent",
    )

    # =====================================================
    # Readonly
    # =====================================================

    readonly_fields = (
        "slug",
        "image_preview",
        "created_at",
        "updated_at",
    )

    # =====================================================
    # Fieldsets
    # =====================================================

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

    # =====================================================
    # Parent
    # =====================================================

    @admin.display(
        description="دسته والد",
        ordering="parent__name",
    )
    def parent_display(self, obj):

        if obj.parent:
            return obj.parent.name

        return "-"

    # =====================================================
    # Image Preview
    # =====================================================

    @admin.display(
        description="پیش‌نمایش تصویر",
    )
    def image_preview(self, obj):

        if not obj.image:
            return "بدون تصویر"

        return format_html(
            '<img src="{}" '
            'width="80" '
            'height="80" '
            'style="object-fit:cover;'
            'border-radius:8px;" />',
            obj.image.url,
        )