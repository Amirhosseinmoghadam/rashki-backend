from django.contrib import admin
from django.utils import timezone

from .forms import DiscountCodeAdminForm

from .models import (
    DiscountCode,
    DiscountUsage,
)


# =========================================================
# Discount Code Admin
# =========================================================


@admin.register(DiscountCode)
class DiscountCodeAdmin(
    admin.ModelAdmin
):

    form = DiscountCodeAdminForm

    list_display = (
        "id",
        "code",
        "discount_display",
        "scope",
        "is_active",
        "usage_display",
        "start_at",
        "end_at",
    )

    list_display_links = (
        "id",
        "code",
    )

    list_filter = (
        "discount_type",
        "scope",
        "is_active",
        "start_at",
        "end_at",
    )

    search_fields = (
        "code",
        "description",
    )

    # برای 10 هزار Product از filter_horizontal
    # استفاده نمی‌کنیم چون همه Productها را Load می‌کند.
    autocomplete_fields = (
        "products",
        "categories",
    )

    readonly_fields = (
        "usage_count_display",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    actions = (
        "activate_codes",
        "deactivate_codes",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "code",
                    "description",
                    "is_active",
                ),
            },
        ),
        (
            "نوع و مقدار تخفیف",
            {
                "fields": (
                    "discount_type",
                    "percentage",
                    "fixed_amount_toman",
                    "minimum_order_toman",
                    "maximum_discount_toman",
                ),
            },
        ),
        (
            "دامنه تخفیف",
            {
                "fields": (
                    "scope",
                    "products",
                    "categories",
                ),
            },
        ),
        (
            "زمان",
            {
                "fields": (
                    "start_at",
                    "end_at",
                ),
            },
        ),
        (
            "محدودیت استفاده",
            {
                "fields": (
                    "usage_limit",
                    "usage_limit_per_user",
                    "usage_count_display",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
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

    @admin.display(
        description="تخفیف"
    )
    def discount_display(
        self,
        obj,
    ):

        if (
            obj.discount_type
            == DiscountCode
            .DiscountType
            .PERCENTAGE
        ):

            return (
                f"{obj.percentage}%"
            )

        return (
            f"{obj.fixed_amount_toman:,} تومان"
        )

    @admin.display(
        description="مصرف"
    )
    def usage_display(
        self,
        obj,
    ):

        used = obj.usages.filter(
            status=(
                DiscountUsage.Status.USED
            )
        ).count()

        if obj.usage_limit is None:

            return f"{used:,}"

        return (
            f"{used:,} / "
            f"{obj.usage_limit:,}"
        )

    @admin.display(
        description="تعداد استفاده فعال"
    )
    def usage_count_display(
        self,
        obj,
    ):

        if not obj.pk:
            return 0

        return obj.usages.filter(
            status=(
                DiscountUsage.Status.USED
            )
        ).count()

    @admin.action(
        description="فعال کردن کدهای انتخاب‌شده"
    )
    def activate_codes(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_active=True
        )

    @admin.action(
        description="غیرفعال کردن کدهای انتخاب‌شده"
    )
    def deactivate_codes(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_active=False
        )


# =========================================================
# Discount Usage Admin
# =========================================================


@admin.register(DiscountUsage)
class DiscountUsageAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "code_snapshot",
        "user",
        "reference",
        "formatted_discount",
        "status",
        "used_at",
    )

    list_filter = (
        "status",
        "used_at",
    )

    search_fields = (
        "code_snapshot",
        "reference",
        "user__phone_number",
    )

    list_select_related = (
        "discount",
        "user",
    )

    readonly_fields = (
        "discount",
        "user",
        "reference",
        "code_snapshot",
        "subtotal_toman",
        "eligible_subtotal_toman",
        "discount_amount_toman",
        "status",
        "used_at",
        "revoked_at",
    )

    ordering = (
        "-used_at",
    )

    list_per_page = 50

    @admin.display(
        description="مبلغ تخفیف"
    )
    def formatted_discount(
        self,
        obj,
    ):

        return (
            f"{obj.discount_amount_toman:,} "
            f"تومان"
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

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        return False