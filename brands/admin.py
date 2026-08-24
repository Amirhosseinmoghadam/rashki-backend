from django.contrib import admin

from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "is_active",
        "created_at",
        "updated_at",
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
        "website",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = ("is_active",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("name",)

    fieldsets = (
        (
            "اطلاعات برند",
            {
                "fields": (
                    "name",
                    "slug",
                    "logo",
                    "description",
                    "website",
                )
            },
        ),
        (
            "وضعیت",
            {"fields": ("is_active",)},
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
