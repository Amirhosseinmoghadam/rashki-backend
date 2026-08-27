from django.contrib import admin

from .models import Order, OrderItem

# =========================================================
# Order Item Inline
# =========================================================


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "unit_price",
        "quantity",
        "discount_amount",
        "total_amount",
    )

    fields = (
        "product_name",
        "sku",
        "unit_price",
        "quantity",
        "discount_amount",
        "total_amount",
    )


# =========================================================
# Order Admin
# =========================================================


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "subtotal",
        "discount_amount",
        "shipping_amount",
        "total_amount",
        "coupon_code",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "address__postal_code",
        "notes",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    inlines = (OrderItemInline,)

    fieldsets = (
        (
            "اطلاعات سفارش",
            {
                "fields": (
                    "user",
                    "address",
                    "status",
                )
            },
        ),
        (
            "مبالغ",
            {
                "fields": (
                    "subtotal",
                    "discount_amount",
                    "shipping_amount",
                    "total_amount",
                    "coupon_code",
                )
            },
        ),
        (
            "یادداشت‌ها",
            {
                "fields": ("notes",),
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


# =========================================================
# Order Item Admin
# =========================================================


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "variant",
        "product_name",
        "sku",
        "unit_price",
        "quantity",
        "discount_amount",
        "total_amount",
    )

    list_filter = (
        "order",
        "product",
    )

    search_fields = (
        "order__id",
        "product__name",
        "variant__sku",
        "product_name",
        "sku",
    )

    autocomplete_fields = (
        "order",
        "product",
        "variant",
    )

    readonly_fields = ("total_amount",)

    ordering = ("-order__created_at",)
