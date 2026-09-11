from django.contrib import (
    admin,
    messages,
)

from .models import (
    ExchangeRate,
    PricingSettings,
)

from .services import (
    activate_exchange_rate,
    recalculate_fixed_products,
    recalculate_usd_products,
)


# =========================================================
# Exchange Rate Admin
# =========================================================


@admin.register(ExchangeRate)
class ExchangeRateAdmin(
    admin.ModelAdmin
):

    # =====================================================
    # List
    # =====================================================

    list_display = (
        "id",
        "currency",
        "formatted_rate",
        "is_active",
        "effective_at",
        "created_by",
        "created_at",
    )

    list_filter = (
        "currency",
        "is_active",
        "effective_at",
    )

    search_fields = (
        "currency",
        "note",
    )

    ordering = (
        "-effective_at",
        "-created_at",
    )

    list_per_page = 50

    # =====================================================
    # Readonly
    # =====================================================

    readonly_fields = (
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    )

    # =====================================================
    # Fields
    # =====================================================

    fieldsets = (
        (
            "نرخ ارز",
            {
                "fields": (
                    "currency",
                    "rate_toman",
                    "effective_at",
                    "note",
                ),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_by",
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
    # Actions
    # =====================================================

    actions = (
        "activate_rate_and_update_prices",
        "recalculate_current_usd_prices",
    )

    # =====================================================
    # Created By
    # =====================================================

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):

        # اگر Rate برای اولین بار ساخته می‌شود،
        # User ثبت‌کننده ذخیره می‌شود.
        if (
            obj.created_by_id is None
            and request.user.is_authenticated
        ):

            obj.created_by = (
                request.user
            )

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # =====================================================
    # Rate Display
    # =====================================================

    @admin.display(
        description="نرخ",
        ordering="rate_toman",
    )
    def formatted_rate(
        self,
        obj,
    ):

        return (
            f"{obj.rate_toman:,} تومان"
        )

    # =====================================================
    # Activate
    # =====================================================

    @admin.action(
        description=(
            "فعال کردن نرخ انتخاب‌شده "
            "و بروزرسانی قیمت محصولات"
        )
    )
    def activate_rate_and_update_prices(
        self,
        request,
        queryset,
    ):

        # فقط یک Rate باید انتخاب شود.
        if queryset.count() != 1:

            self.message_user(
                request,
                (
                    "برای فعال‌سازی نرخ "
                    "فقط یک رکورد را انتخاب کنید."
                ),
                level=messages.ERROR,
            )

            return

        exchange_rate = queryset.first()

        try:

            updated_count = (
                activate_exchange_rate(
                    exchange_rate
                )
            )

        except Exception as exc:

            self.message_user(
                request,
                f"خطا در بروزرسانی قیمت‌ها: {exc}",
                level=messages.ERROR,
            )

            return

        self.message_user(
            request,
            (
                f"نرخ {exchange_rate.currency} "
                f"با مقدار "
                f"{exchange_rate.rate_toman:,} تومان "
                f"فعال شد و قیمت "
                f"{updated_count:,} محصول "
                f"بروزرسانی شد."
            ),
            level=messages.SUCCESS,
        )

    # =====================================================
    # Recalculate
    # =====================================================

    @admin.action(
        description=(
            "محاسبه مجدد محصولات "
            "با نرخ فعال فعلی"
        )
    )
    def recalculate_current_usd_prices(
        self,
        request,
        queryset,
    ):

        try:

            updated_count = (
                recalculate_usd_products()
            )

        except Exception as exc:

            self.message_user(
                request,
                f"خطا در محاسبه قیمت‌ها: {exc}",
                level=messages.ERROR,
            )

            return

        self.message_user(
            request,
            (
                f"قیمت {updated_count:,} "
                f"محصول دلاری "
                f"بروزرسانی شد."
            ),
            level=messages.SUCCESS,
        )


# =========================================================
# Pricing Settings Admin
# =========================================================


@admin.register(PricingSettings)
class PricingSettingsAdmin(
    admin.ModelAdmin
):

    list_display = (
        "rounding_step_toman",
        "rounding_mode",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (
        (
            "گردکردن قیمت",
            {
                "fields": (
                    "rounding_step_toman",
                    "rounding_mode",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "updated_at",
                ),
            },
        ),
    )

    actions = (
        "recalculate_all_prices",
    )

    # فقط یک PricingSettings قابل ساخت است.
    def has_add_permission(
        self,
        request,
    ):

        if PricingSettings.objects.exists():

            return False

        return super().has_add_permission(
            request
        )

    # تنظیمات Pricing قابل حذف نیست.
    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        return False

    @admin.action(
        description=(
            "محاسبه مجدد تمام قیمت‌ها "
            "با تنظیمات جدید"
        )
    )
    def recalculate_all_prices(
        self,
        request,
        queryset,
    ):

        try:

            usd_count = (
                recalculate_usd_products()
            )

            fixed_count = (
                recalculate_fixed_products()
            )

        except Exception as exc:

            self.message_user(
                request,
                f"خطا در محاسبه قیمت‌ها: {exc}",
                level=messages.ERROR,
            )

            return

        total = (
            usd_count
            + fixed_count
        )

        self.message_user(
            request,
            (
                f"قیمت {total:,} محصول "
                f"بروزرسانی شد."
            ),
            level=messages.SUCCESS,
        )