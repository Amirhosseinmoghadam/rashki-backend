

# Register your models here.
from django.contrib import admin

from addresses.models import Province, City



from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin,
)

from .models import (
    User,
    Address,
)


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin options for the Province model."""

    list_display = ("name", "id")
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin options for the City model."""

    list_display = ("name", "province", "id")
    search_fields = ("name", "province__name")
    list_filter = ("province",)
    ordering = ("province", "name")





# =========================================================
# Address Admin
# =========================================================


# @admin.register(Address)
# class AddressAdmin(admin.ModelAdmin):
#
#     list_display = (
#         "user",
#         "first_name",
#         "last_name",
#         "mobile_number",
#         "province",
#         "city",
#         "is_default",
#         "created_at",
#     )
#
#     list_filter = (
#         "is_default",
#         "province",
#         "city",
#     )
#
#     search_fields = (
#         "user__phone_number",
#         "first_name",
#         "last_name",
#         "mobile_number",
#         "postal_code",
#     )
#
#     ordering = ("-created_at",)


from django.utils.html import format_html

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # =====================================================
    # List Display
    # =====================================================

    list_display = (
        "id",
        "user_display",
        "full_name",
        "mobile_number",
        "province",
        "city",
        "default_status",
        "created_at",
    )

    # =====================================================
    # List Filters
    # =====================================================

    list_filter = (
        "is_default",
        "province",
        "city",
        "created_at",
    )

    # =====================================================
    # Search
    # =====================================================

    search_fields = (
        "first_name",
        "last_name",
        "mobile_number",
        "phone_number",
        "postal_code",
        "postal_address",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
    )

    # =====================================================
    # Ordering
    # =====================================================

    ordering = (
        "-is_default",
        "-created_at",
    )

    # =====================================================
    # Pagination
    # =====================================================

    list_per_page = 25

    # =====================================================
    # Related Object Optimization
    # =====================================================

    list_select_related = (
        "user",
        "province",
        "city",
    )

    # =====================================================
    # Autocomplete
    # =====================================================

    autocomplete_fields = (
        "user",
        "province",
        "city",
    )

    # =====================================================
    # Read Only Fields
    # =====================================================

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # =====================================================
    # Fieldsets
    # =====================================================

    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "اطلاعات گیرنده",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "mobile_number",
                    "phone_number",

                )
            },
        ),
        (
            "اطلاعات آدرس",
            {
                "fields": (
                    "province",
                    "city",
                    "postal_code",
                    "postal_address",
                )
            },
        ),
        (
            "تنظیمات",
            {
                "fields": (
                    "is_default",
                )
            },
        ),
        (
            "اطلاعات سیستم",
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
    # Custom Display Methods
    # =====================================================

    @admin.display(
        description="کاربر",
        ordering="user",
    )
    def user_display(self, obj):
        if not obj.user:
            return "-"

        if hasattr(obj.user, "phone_number"):
            return obj.user.phone_number

        return str(obj.user)

    @admin.display(
        description="نام گیرنده",
        ordering="first_name",
    )
    def full_name(self, obj):
        full_name = (
            f"{obj.first_name or ''} "
            f"{obj.last_name or ''}"
        ).strip()

        return full_name or "-"

    @admin.display(
        description="پیش‌فرض",
        boolean=True,
        ordering="is_default",
    )
    def default_status(self, obj):
        return obj.is_default