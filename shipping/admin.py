from django.contrib import admin


from .models import (
    Shipment,
    ShippingMethod,

    ShippingRateRule,
    ShippingSettings,
    TipaxPackageProfile,
    TipaxSettings,
)

from django.contrib import admin, messages
from django.db import transaction

from shipping.models import (
    ShippingOrigin,
    ShippingProviderCity,
    ShippingProviderCityMap,
    ShippingProviderPackingOption,
    ShippingProviderProvince,
    ShippingProviderProvinceMap,
)
# =========================================================
# Rate Inline
# =========================================================


class ShippingRateRuleInline(
    admin.TabularInline
):

    model = ShippingRateRule

    extra = 0

    autocomplete_fields = (
        "province",
        "city",
    )

    fields = (
        "destination_scope",
        "province",
        "city",
        "min_weight_grams",
        "max_weight_grams",
        "base_price_toman",
        "included_weight_grams",
        "additional_per_kg_toman",
        "priority",
        "is_active",
    )


# =========================================================
# Shipping Method
# =========================================================


@admin.register(ShippingMethod)
class ShippingMethodAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "name",
        "code",
        "provider",
        "service_code",
        "calculation_mode",
        "delivery_time",
        "is_active",
        "sort_order",
    )

    list_filter = (
        "provider",
        "calculation_mode",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "service_code",
    )

    ordering = (
        "sort_order",
        "id",
    )

    inlines = (
        ShippingRateRuleInline,
    )

    @admin.display(
        description="زمان تقریبی تحویل"
    )
    def delivery_time(
        self,
        obj,
    ):

        if (
            obj.estimated_min_days is None
            and obj.estimated_max_days is None
        ):
            return "-"

        if (
            obj.estimated_min_days
            == obj.estimated_max_days
        ):
            return (
                f"{obj.estimated_min_days} روز"
            )

        return (
            f"{obj.estimated_min_days or '?'} "
            f"تا "
            f"{obj.estimated_max_days or '?'} روز"
        )


# =========================================================
# Rate Rule
# =========================================================


@admin.register(ShippingRateRule)
class ShippingRateRuleAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "method",
        "destination_scope",
        "destination_display",
        "weight_range",
        "formatted_base_price",
        "additional_per_kg_toman",
        "priority",
        "is_active",
    )

    list_filter = (
        "method",
        "destination_scope",
        "is_active",
        "effective_from",
    )

    search_fields = (
        "method__name",
        "province__name",
        "city__name",
        "note",
    )

    autocomplete_fields = (
        "method",
        "province",
        "city",
    )

    list_select_related = (
        "method",
        "province",
        "city",
    )

    ordering = (
        "-priority",
        "-effective_from",
    )

    @admin.display(
        description="مقصد"
    )
    def destination_display(
        self,
        obj,
    ):

        if obj.city_id:
            return obj.city.name

        if obj.province_id:
            return obj.province.name

        return "کل کشور"

    @admin.display(
        description="بازه وزن"
    )
    def weight_range(
        self,
        obj,
    ):

        maximum = (
            f"{obj.max_weight_grams:,}"
            if obj.max_weight_grams
            is not None
            else "∞"
        )

        return (
            f"{obj.min_weight_grams:,} "
            f"تا {maximum} گرم"
        )

    @admin.display(
        description="هزینه پایه",
        ordering="base_price_toman",
    )
    def formatted_base_price(
        self,
        obj,
    ):

        return (
            f"{obj.base_price_toman:,} تومان"
        )


# =========================================================
# Settings
# =========================================================


@admin.register(ShippingSettings)
class ShippingSettingsAdmin(
    admin.ModelAdmin
):

    list_display = (
        "origin_city",
        "package_extra_weight_grams",
        "updated_at",
    )

    autocomplete_fields = (
        "origin_city",
    )

    readonly_fields = (
        "updated_at",
    )

    def has_add_permission(
        self,
        request,
    ):

        if ShippingSettings.objects.exists():
            return False

        return super().has_add_permission(
            request
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        return False

# =========================================================
# Provider City Mapping
# =========================================================


@admin.register(
    ShippingProviderCityMap
)
class ShippingProviderCityMapAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "provider",
        "local_province",
        "city",
        "provider_city_name",
        "provider_city_id",
        "is_active",
    )

    list_filter = (
        "provider",
        "is_active",
        "city__province",
    )

    search_fields = (
        "city__name",
        "city__province__name",
        "provider_city_name",
        "provider_city_id",
    )

    autocomplete_fields = (
        "city",
    )

    ordering = (
        "city__province__name",
        "city__name",
    )

    list_select_related = (
        "city",
        "city__province",
    )

    list_per_page = 100

    actions = (
        "activate_maps",
        "deactivate_maps",
    )

    @admin.display(
        description="استان داخلی",
        ordering="city__province__name",
    )
    def local_province(
        self,
        obj,
    ):

        return obj.city.province.name

    @admin.action(
        description="فعال کردن Mapهای انتخاب‌شده"
    )
    def activate_maps(
        self,
        request,
        queryset,
    ):

        count = queryset.update(
            is_active=True
        )

        self.message_user(
            request,
            f"{count} Map فعال شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="غیرفعال کردن Mapهای انتخاب‌شده"
    )
    def deactivate_maps(
        self,
        request,
        queryset,
    ):

        count = queryset.update(
            is_active=False
        )

        self.message_user(
            request,
            f"{count} Map غیرفعال شد.",
            level=messages.SUCCESS,
        )


# =========================================================
# Tipax Package Profile
# =========================================================


@admin.register(
    TipaxPackageProfile
)
class TipaxPackageProfileAdmin(
    admin.ModelAdmin
):

    list_display = (
        "title",
        "min_weight_grams",
        "max_weight_grams",
        "pack_type",
        "package_content_id",
        "packing_id",
        "priority",
        "is_active",
    )

    list_filter = (
        "pack_type",
        "is_active",
    )


# =========================================================
# Tipax Settings
# =========================================================


@admin.register(
    TipaxSettings
)
class TipaxSettingsAdmin(
    admin.ModelAdmin
):

    list_display = (
        "sender_full_name",
        "sender_mobile",
        "payment_type",
        "pickup_type",
        "distribution_type",
        "default_service_id",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )

    def has_add_permission(
        self,
        request,
    ):

        if TipaxSettings.objects.exists():
            return False

        return super().has_add_permission(
            request
        )

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        return False


# =========================================================
# Shipment
# =========================================================


@admin.register(
    Shipment
)
class ShipmentAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "order",
        "provider",
        "status",
        "external_order_id",
        "primary_tracking_code",
        "provider_status_name",
        "created_at",
    )

    list_filter = (
        "provider",
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "external_order_id",
        "primary_tracking_code",
    )

    list_select_related = (
        "order",
        "shipping_method",
    )

    readonly_fields = [
        field.name
        for field
        in Shipment._meta.fields
    ]

    def has_add_permission(
        self,
        request,
    ):

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        return False



@admin.register(ShippingOrigin)
class ShippingOriginAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "province",
        "city",
        "is_default",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_default",
        "is_active",
        "province",
    )

    search_fields = (
        "title",
        "province__name",
        "city__name",
        "postal_address",
        "postal_code",
    )

    autocomplete_fields = (
        "province",
        "city",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-is_default",
        "title",
    )

    fieldsets = (
        (
            "مشخصات مبدا",
            {
                "fields": (
                    "title",
                    "province",
                    "city",
                    "postal_address",
                    "postal_code",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                    "is_default",
                )
            },
        ),
        (
            "تاریخ‌ها",
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

    actions = (
        "set_as_default",
        "activate_origins",
        "deactivate_origins",
    )

    @admin.action(
        description="قرار دادن به عنوان مبدا پیش‌فرض"
    )
    def set_as_default(
        self,
        request,
        queryset,
    ):

        if queryset.count() != 1:

            self.message_user(
                request,
                (
                    "برای تعیین مبدا پیش‌فرض "
                    "فقط یک مورد را انتخاب کنید."
                ),
                level=messages.ERROR,
            )

            return

        origin = queryset.first()

        if not origin.is_active:

            origin.is_active = True

        origin.is_default = True
        origin.save()

        self.message_user(
            request,
            (
                f"«{origin.title}» به عنوان "
                "مبدا پیش‌فرض انتخاب شد."
            ),
            level=messages.SUCCESS,
        )

    @admin.action(
        description="فعال کردن مبداهای انتخاب‌شده"
    )
    def activate_origins(
        self,
        request,
        queryset,
    ):

        count = queryset.update(
            is_active=True
        )

        self.message_user(
            request,
            f"{count} مبدا فعال شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="غیرفعال کردن مبداهای انتخاب‌شده"
    )
    def deactivate_origins(
        self,
        request,
        queryset,
    ):

        if queryset.filter(
            is_default=True
        ).exists():

            self.message_user(
                request,
                (
                    "مبدا پیش‌فرض را نمی‌توان "
                    "غیرفعال کرد. ابتدا مبدا دیگری "
                    "را پیش‌فرض کنید."
                ),
                level=messages.ERROR,
            )

            return

        count = queryset.update(
            is_active=False
        )

        self.message_user(
            request,
            f"{count} مبدا غیرفعال شد.",
            level=messages.SUCCESS,
        )


@admin.register(
    ShippingProviderProvince
)
class ShippingProviderProvinceAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "provider",
        "provider_province_id",
        "name",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "provider",
        "is_active",
    )

    search_fields = (
        "provider_province_id",
        "name",
    )

    readonly_fields = (
        "provider",
        "provider_province_id",
        "name",
        "raw_data",
        "created_at",
        "updated_at",
    )

    ordering = (
        "provider",
        "provider_province_id",
    )


@admin.register(
    ShippingProviderCity
)
class ShippingProviderCityAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "name",
        "provider",
        "provider_city_id",
        "provider_province_id",
        "is_active",
    )

    list_filter = (
        "provider",
        "is_active",
        "provider_province_id",
    )

    search_fields = (
        "name",
        "provider_city_id",
        "provider_uuid",
    )

    readonly_fields = (
        "provider",
        "provider_city_id",
        "provider_province_id",
        "name",
        "provider_uuid",
        "latitude",
        "longitude",
        "raw_data",
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )

    list_per_page = 100


@admin.register(
    ShippingProviderProvinceMap
)
class ShippingProviderProvinceMapAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "provider",
        "province",
        "provider_province_name",
        "provider_province_id",
        "is_active",
    )

    list_filter = (
        "provider",
        "is_active",
    )

    search_fields = (
        "province__name",
        "provider_province_name",
        "provider_province_id",
    )

    autocomplete_fields = (
        "province",
    )

    ordering = (
        "province__name",
    )

    actions = (
        "activate_maps",
        "deactivate_maps",
    )

    @admin.action(
        description="فعال کردن Mapهای انتخاب‌شده"
    )
    def activate_maps(
        self,
        request,
        queryset,
    ):

        count = queryset.update(
            is_active=True
        )

        self.message_user(
            request,
            f"{count} Map فعال شد.",
            level=messages.SUCCESS,
        )

    @admin.action(
        description="غیرفعال کردن Mapهای انتخاب‌شده"
    )
    def deactivate_maps(
        self,
        request,
        queryset,
    ):

        count = queryset.update(
            is_active=False
        )

        self.message_user(
            request,
            f"{count} Map غیرفعال شد.",
            level=messages.SUCCESS,
        )


@admin.register(
    ShippingProviderPackingOption
)
class ShippingProviderPackingOptionAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "provider",
        "box_number",
        "title",
        "provider_packing_id",
        "kind",
        "dimensions_display",
        "weight_range_display",
        "provider_price",
        "is_active",
    )

    list_filter = (
        "provider",
        "kind",
        "is_active",
        "pack_type",
    )

    search_fields = (
        "title",
        "provider_packing_id",
        "box_number",
    )

    ordering = (
        "provider",
        "kind",
        "box_number",
        "provider_packing_id",
    )

    readonly_fields = (
        "provider",
        "provider_packing_id",
        "title",
        "kind",
        "box_number",
        "pack_type",
        "length",
        "width",
        "height",
        "min_weight",
        "max_weight",
        "min_length",
        "max_length",
        "min_width",
        "max_width",
        "min_height",
        "max_height",
        "provider_price",
        "raw_data",
        "created_at",
        "updated_at",
    )

    list_per_page = 100

    @admin.display(
        description="ابعاد"
    )
    def dimensions_display(
        self,
        obj,
    ):

        if (
            obj.length is None
            or obj.width is None
            or obj.height is None
        ):
            return "-"

        return (
            f"{obj.length} × "
            f"{obj.width} × "
            f"{obj.height} cm"
        )

    @admin.display(
        description="محدوده وزن"
    )
    def weight_range_display(
        self,
        obj,
    ):

        if (
            obj.min_weight is None
            and obj.max_weight is None
        ):
            return "-"

        return (
            f"{obj.min_weight or '-'} "
            f"تا "
            f"{obj.max_weight or '-'}"
        )


