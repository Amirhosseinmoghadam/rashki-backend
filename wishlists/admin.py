from django.contrib import admin

from .models import WishlistItem


# =========================================================
# Wishlist Admin
# =========================================================


@admin.register(WishlistItem)
class WishlistItemAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "user",
        "product",
        "created_at",
    )

    list_display_links = (
        "id",
        "product",
    )

    search_fields = (
        "user__phone_number",
        "product__name",
        "product__sku",
        "product__manufacturer_part_number",
        "product__oem_code",
    )

    list_filter = (
        "created_at",
    )

    list_select_related = (
        "user",
        "product",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    readonly_fields = (
        "user",
        "product",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    # Wishlist باید توسط خود User ساخته شود،
    # نه به صورت دستی توسط Admin.
    def has_add_permission(
        self,
        request,
    ):

        return False