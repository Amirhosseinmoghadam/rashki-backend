from django.contrib import admin

from .models import Cart, CartItem


# =========================================================
# Cart Item Inline
# =========================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

    autocomplete_fields = (
        "variant",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fields = (
        "variant",
        "quantity",
        "created_at",
        "updated_at",
    )


# =========================================================
# Cart
# =========================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "items_count",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "user__mobile_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "user",
    )

    ordering = (
        "-updated_at",
    )

    inlines = (
        CartItemInline,
    )

    fieldsets = (
        (
            "اطلاعات سبد خرید",
            {
                "fields": (
                    "user",
                )
            },
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

    @admin.display(
        description="تعداد آیتم‌ها",
    )
    def items_count(self, obj):
        return obj.items.count()


# =========================================================
# Cart Item
# =========================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "variant",
        "quantity",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "cart__user__username",
        "cart__user__email",
        "cart__user__first_name",
        "cart__user__last_name",
        "variant__sku",
        "variant__product__name",
    )

    autocomplete_fields = (
        "cart",
        "variant",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-updated_at",
    )