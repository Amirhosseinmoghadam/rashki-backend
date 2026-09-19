from django.contrib import admin

from addresses.models import Address, City, Province


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "province")
    search_fields = ("name", "province__name")
    list_filter = ("province",)
    ordering = ("province__name", "name")
    autocomplete_fields = ("province",)
    list_select_related = ("province",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_display",
        "full_name",
        "mobile_number",
        "province",
        "city",
        "is_default",
        "created_at",
    )

    list_filter = (
        "is_default",
        "province",
        "city",
        "created_at",
    )

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

    ordering = ("-is_default", "-created_at")
    list_per_page = 25

    list_select_related = (
        "user",
        "province",
        "city",
    )

    autocomplete_fields = (
        "user",
        "province",
        "city",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات کاربر",
            {"fields": ("user",)},
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
            {"fields": ("is_default",)},
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

    @admin.display(
        description="کاربر",
        ordering="user__phone_number",
    )
    def user_display(self, obj):
        return (
            getattr(
                obj.user,
                "phone_number",
                None,
            )
            or str(obj.user)
        )

    @admin.display(
        description="نام گیرنده",
        ordering="first_name",
    )
    def full_name(self, obj):
        return (
            f"{obj.first_name or ''} "
            f"{obj.last_name or ''}"
        ).strip() or "-"
