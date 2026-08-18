from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin,
)

from .models import (
    User,
    OTPCode,
    Address,
)

# =========================================================
# User Admin
# =========================================================


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "is_phone_verified",
        "is_profile_completed",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "is_phone_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "phone_number",
        "first_name",
        "last_name",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "phone_number",
        "date_joined",
        "created_at",
        "updated_at",
        "last_login",
    )

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "phone_number",
                    "password",
                    "is_phone_verified",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "User Information",
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


# =========================================================
# OTP Admin
# =========================================================


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):

    list_display = (
        "phone_number",
        "purpose",
        "attempts",
        "max_attempts",
        "is_used",
        "expires_at",
        "created_at",
    )

    list_filter = (
        "purpose",
        "is_used",
    )

    search_fields = ("phone_number",)

    readonly_fields = (
        "phone_number",
        "code_hash",
        "purpose",
        "attempts",
        "max_attempts",
        "is_used",
        "expires_at",
        "created_at",
    )

    ordering = ("-created_at",)


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

from django.contrib import admin
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
        "email",
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
                    "email",
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