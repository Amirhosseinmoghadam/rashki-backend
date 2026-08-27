from django.contrib import admin

from .models import (
    Product,
    ProductImage,
    AttributeGroup,
    Attribute,
    AttributeValue,
    ProductAttributeValue,
    ProductVariant,
    VariantAttributeValue,
    ProductMotorcycleCompatibility,
)

# =========================================================
# Product Admin
# =========================================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    مدیریت محصولات در پنل Django Admin.
    """

    list_display = (
        "name",
        "brand",
        "category",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "brand",
        "category",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                    "brand",
                    "category",
                )
            },
        ),
        (
            "توضیحات",
            {
                "fields": (
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
            "تاریخ‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# =========================================================
# Product Image Admin
# =========================================================


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    مدیریت تصاویر محصولات.
    """

    list_display = (
        "product",
        "alt_text",
        "caption",
        "is_primary",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_primary",
        "product",
    )

    search_fields = (
        "product__name",
        "alt_text",
        "caption",
    )

    readonly_fields = ("created_at",)

    ordering = (
        "product",
        "sort_order",
    )


# =========================================================
# Attribute Group Admin
# =========================================================


@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    """
    مدیریت گروه‌های ویژگی.

    مثال:
        مشخصات فنی
        ابعاد
        ظاهری
        عملکرد
    """

    list_display = (
        "name",
        "slug",
        "sort_order",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = (
        "sort_order",
        "name",
    )


# =========================================================
# Attribute Admin
# =========================================================


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """
    مدیریت ویژگی‌های محصولات.

    نکته:
    slug توسط prepopulated_fields از روی name
    در پنل Admin پیشنهاد می‌شود.

    همچنین در مدل Attribute نیز در متد save()
    در صورت خالی بودن slug، مقدار آن به صورت خودکار
    ساخته می‌شود.
    """

    list_display = (
        "name",
        "group",
        "value_type",
        "unit",
        "is_filterable",
        "is_required",
        "sort_order",
        "is_active",
    )

    list_filter = (
        "value_type",
        "is_filterable",
        "is_required",
        "is_active",
        "group",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = (
        "group",
        "sort_order",
        "name",
    )


# =========================================================
# Attribute Value Admin
# =========================================================


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    """
    مدیریت مقادیر مربوط به ویژگی‌ها.

    مثال:

        Attribute:
            رنگ

        AttributeValue:
            مشکی
            سفید
            قرمز
    """

    list_display = (
        "attribute",
        "value",
        "slug",
        "sort_order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "attribute",
    )

    search_fields = (
        "value",
        "slug",
        "attribute__name",
    )

    prepopulated_fields = {
        "slug": ("value",),
    }

    ordering = (
        "attribute",
        "sort_order",
        "value",
    )


# =========================================================
# Product Attribute Value Admin
# =========================================================


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """
    ویژگی‌هایی که مستقیماً به Product مربوط هستند
    و بین Variantهای مختلف محصول مشترک هستند.
    """

    list_display = (
        "product",
        "attribute",
        "value",
    )

    list_filter = ("attribute",)

    search_fields = (
        "product__name",
        "attribute__name",
        "value",
    )

    autocomplete_fields = (
        "product",
        "attribute",
    )


# =========================================================
# Product Variant Admin
# =========================================================


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    مدیریت Variantهای محصول.

    هر Variant می‌تواند قیمت، موجودی و SKU
    مستقل داشته باشد.
    """

    list_display = (
        "product",
        "name",
        "sku",
        "price",
        "stock",
        "is_active",
        "is_in_stock",
        "created_at",
    )

    list_filter = (
        "is_active",
        "product",
    )

    search_fields = (
        "product__name",
        "sku",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "is_in_stock",
        "is_available",
    )

    autocomplete_fields = ("product",)

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "product",
                    "name",
                    "sku",
                )
            },
        ),
        (
            "قیمت و موجودی",
            {
                "fields": (
                    "price",
                    "stock",
                )
            },
        ),
        (
            "وضعیت",
            {"fields": ("is_active",)},
        ),
        (
            "اطلاعات اضافی",
            {
                "fields": (
                    "is_in_stock",
                    "is_available",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = (
        "product",
        "id",
    )


# =========================================================
# Variant Attribute Value Admin
# =========================================================


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    """
    مدیریت ویژگی‌های اختصاصی هر Variant.

    مثال:

        Variant:
            CG125 - جلو - مشکی

        Attributes:
            مدل موتور = CG125
            محل نصب = جلو
            رنگ = مشکی
    """

    list_display = (
        "variant",
        "attribute",
        "value",
    )

    list_filter = ("attribute",)

    search_fields = (
        "variant__sku",
        "variant__name",
        "attribute__name",
        "value__value",
    )

    autocomplete_fields = (
        "variant",
        "attribute",
        "value",
    )


# =========================================================
# Product Motorcycle Compatibility Admin
# =========================================================


@admin.register(ProductMotorcycleCompatibility)
class ProductMotorcycleCompatibilityAdmin(admin.ModelAdmin):
    """
    مدیریت سازگاری محصولات با موتورسیکلت‌ها.

    مثال:

        محصول:
            لنت ترمز

        موتورسیکلت:
            Honda CG125
    """

    list_display = (
        "product",
        "motorcycle",
        "note",
    )

    list_filter = ("motorcycle",)

    search_fields = (
        "product__name",
        "motorcycle__name",
    )

    autocomplete_fields = (
        "product",
        "motorcycle",
    )
