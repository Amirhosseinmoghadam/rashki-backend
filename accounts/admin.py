from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin,
)

from .models import (
    User,
    OTPCode,

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


