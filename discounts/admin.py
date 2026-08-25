from django.contrib import admin

from .models import Discount, Coupon


# =========================================================
# Discount Admin
# =========================================================


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_type",
        "value",
        "starts_at",
        "ends_at",
        "is_active",
        "created_at",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "starts_at",
        "ends_at",
    )

    search_fields = (
        "name",
        "products__name",
        "categories__name",
    )

    filter_horizontal = (
        "products",
        "categories",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-starts_at",
        "-created_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "discount_type",
                    "value",
                )
            },
        ),
        (
            "محدوده تخفیف",
            {
                "fields": (
                    "products",
                    "categories",
                )
            },
        ),
        (
            "زمان‌بندی",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": ("is_active",)
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )


# =========================================================
# Coupon Admin
# =========================================================


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "minimum_order_amount",
        "maximum_discount_amount",
        "usage_limit",
        "starts_at",
        "ends_at",
        "is_active",
        "created_at",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "starts_at",
        "ends_at",
    )

    search_fields = (
        "code",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-starts_at",
        "-created_at",
    )

    fieldsets = (
        (
            "اطلاعات کد تخفیف",
            {
                "fields": (
                    "code",
                    "discount_type",
                    "value",
                )
            },
        ),
        (
            "محدودیت‌ها",
            {
                "fields": (
                    "minimum_order_amount",
                    "maximum_discount_amount",
                    "usage_limit",
                    "usage_limit_per_user",
                )
            },
        ),
        (
            "زمان‌بندی",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": ("is_active",)
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )