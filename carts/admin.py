from django.contrib import admin

from .models import (
    Cart,
    CartItem,
)


# =========================================================
# Cart Item Inline
# =========================================================


class CartItemInline(
    admin.TabularInline
):

    model = CartItem

    extra = 0

    fields = (
        "product",
        "quantity",
        "created_at",
        "updated_at",
    )

    readonly_fields = fields

    can_delete = False

    show_change_link = False


# =========================================================
# Cart Admin
# =========================================================


@admin.register(Cart)
class CartAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "user",
        "item_count",
        "applied_discount",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__phone_number",
        "applied_discount__code",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "applied_discount",
    )

    readonly_fields = (
        "user",
        "applied_discount",
        "created_at",
        "updated_at",
    )

    inlines = (
        CartItemInline,
    )

    ordering = (
        "-updated_at",
    )

    list_per_page = 50

    @admin.display(
        description="تعداد آیتم"
    )
    def item_count(
        self,
        obj,
    ):

        return obj.items.count()

    def has_add_permission(
        self,
        request,
    ):

        return False


# =========================================================
# Cart Item Admin
# =========================================================


@admin.register(CartItem)
class CartItemAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "cart__user__phone_number",
        "product__name",
        "product__sku",
    )

    list_select_related = (
        "cart",
        "cart__user",
        "product",
    )

    readonly_fields = (
        "cart",
        "product",
        "quantity",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-updated_at",
    )

    def has_add_permission(
        self,
        request,
    ):

        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):

        return False