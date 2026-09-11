from django.contrib import admin, messages
from django.utils.html import format_html

from pricing.services import (
    PricingError,
    recalculate_product_price,
)

from shipping.packaging.selector import (
    PackagingSelectionError,
    select_tipax_carton_for_product,
)

from .forms import ProductAdminForm

from .models import (
    Product,
    ProductImage,
    ProductAttribute,
    ProductAttributeOption,
    CategoryAttribute,
    ProductAttributeValue,
    ProductCompatibility,
    ProductRelation,
)

from django.utils import timezone

from pricing.services import (
    PricingError,
    calculate_product_price,
)

# =========================================================
# Product Image Inline
# =========================================================


class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1

    max_num = ProductImage.MAX_IMAGES_PER_PRODUCT

    fields = (
        "image",
        "image_preview",
        "alt_text",
        "is_primary",
        "sort_order",
    )

    readonly_fields = (
        "image_preview",
    )

    ordering = (
        "sort_order",
        "id",
    )

    @admin.display(
        description="پیش‌نمایش"
    )
    def image_preview(
        self,
        obj,
    ):

        if not obj.pk or not obj.image:
            return "-"

        return format_html(
            '<img src="{}" '
            'width="80" '
            'height="80" '
            'style="'
            'object-fit:cover;'
            'border-radius:8px;'
            '" />',
            obj.image.url,
        )


# =========================================================
# Product Attribute Value Inline
# =========================================================


class ProductAttributeValueInline(
    admin.TabularInline
):

    model = ProductAttributeValue

    extra = 1

    autocomplete_fields = (
        "attribute",
        "option",
    )

    fields = (
        "attribute",
        "value_text",
        "value_number",
        "value_boolean",
        "option",
    )


# =========================================================
# Product Compatibility Inline
# =========================================================


class ProductCompatibilityInline(
    admin.TabularInline
):

    model = ProductCompatibility

    extra = 1

    autocomplete_fields = (
        "motorcycle",
    )

    fields = (
        "motorcycle",
        "compatible_start_year",
        "compatible_end_year",
        "note",
    )


# =========================================================
# Product Relation Inline
# =========================================================


class ProductRelationInline(
    admin.TabularInline
):

    model = ProductRelation

    fk_name = "product"

    extra = 1

    autocomplete_fields = (
        "related_product",
    )

    fields = (
        "related_product",
        "sort_order",
    )


# =========================================================
# Product Admin
# =========================================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "id",
        "name",
        "sku",
        "category",
        "brand",
        "formatted_price",
        "stock_quantity",
        "stock_status",
        "status",
        "is_featured",
        "primary_image_preview",
    )

    list_display_links = (
        "id",
        "name",
    )

    list_filter = (
        "status",
        "pricing_mode",
        "is_featured",
        "is_price_locked",
        "category",
        "brand",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "sku",
        "manufacturer_part_number",
        "oem_code",
        "barcode",
        "search_keywords",
        "brand__name",
        "category__name",
    )

    autocomplete_fields = (
        "category",
        "brand",
    )

    list_select_related = (
        "category",
        "brand",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    readonly_fields = (
        "slug",
        "current_price_toman",
        "last_exchange_rate_toman",
        "price_updated_at",
        "primary_image_preview",
        "created_at",
        "updated_at",
        "tipax_packing_suggestion",
    )

    inlines = (
        ProductImageInline,
        ProductAttributeValueInline,
        ProductCompatibilityInline,
        ProductRelationInline,
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "brand",
                    "unit",
                    "status",
                    "is_featured",
                ),
            },
        ),
        (
            "کدهای محصول",
            {
                "fields": (
                    "sku",
                    "manufacturer_part_number",
                    "oem_code",
                    "barcode",
                ),
            },
        ),
        (
            "توضیحات",
            {
                "fields": (
                    "short_description",
                    "description",
                    "search_keywords",
                ),
            },
        ),
        (
            "قیمت‌گذاری",
            {
                "fields": (
                    "pricing_mode",
                    "base_price_usd",
                    "base_price_toman",
                    "markup_percent",
                    "fixed_cost_toman",
                    "current_price_toman",
                    "last_exchange_rate_toman",
                    "price_updated_at",
                    "is_price_locked",
                ),
            },
        ),
        (
            "موجودی",
            {
                "fields": (
                    "stock_quantity",
                    "low_stock_threshold",
                ),
            },
        ),
        (
            "ارسال",
            {
                "fields": (
                    "weight_grams",
                    "length_cm",
                    "width_cm",
                    "height_cm",
                ),
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                ),
            },
        ),
        (
            "تصویر اصلی",
            {
                "fields": (
                    "primary_image_preview",
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

    actions = (
        "recalculate_selected_prices",
        "mark_as_featured",
        "remove_from_featured",
        "archive_products",
    )

    @admin.display(
        description="بسته پیشنهادی تیپاکس"
    )
    def tipax_packing_suggestion(self, obj):
        if not obj or not obj.pk:
            return "پس از ذخیره محصول محاسبه می‌شود."

        try:
            selection = (
                select_tipax_carton_for_product(
                    product=obj
                )
            )

        except PackagingSelectionError as exc:
            return format_html(
                '<span style="color:#ba2121;">{}</span>',
                str(exc),
            )

        packing = selection.packing

        return format_html(
            (
                '<strong>{}</strong><br>'
                'شماره باکس: {}<br>'
                'Packing ID: {}<br>'
                'ابعاد: {} × {} × {} cm'
            ),
            packing.title,
            packing.box_number or "-",
            packing.provider_packing_id,
            packing.length,
            packing.width,
            packing.height,
        )

    # =====================================================
    # QuerySet
    # =====================================================

    def get_queryset(
        self,
        request,
    ):

        return (
            super()
            .get_queryset(request)
            .select_related(
                "category",
                "brand",
            )
            .prefetch_related(
                "images"
            )
        )

    # =====================================================
    # Price
    # =====================================================

    @admin.display(
        description="قیمت",
        ordering="current_price_toman",
    )
    def formatted_price(
        self,
        obj,
    ):

        if obj.current_price_toman is None:
            return "بدون قیمت"

        return (
            f"{obj.current_price_toman:,} "
            f"تومان"
        )

    # =====================================================
    # Stock
    # =====================================================

    @admin.display(
        description="وضعیت موجودی"
    )
    def stock_status(
        self,
        obj,
    ):

        if obj.stock_quantity == 0:
            return "ناموجود"

        if (
            obj.stock_quantity
            <= obj.low_stock_threshold
        ):
            return "رو به اتمام"

        return "موجود"

    # =====================================================
    # Primary Image
    # =====================================================

    @admin.display(
        description="تصویر اصلی"
    )
    def primary_image_preview(
        self,
        obj,
    ):

        if not obj.pk:
            return "-"

        image = next(
            (
                image
                for image in obj.images.all()
                if image.is_primary
            ),
            None,
        )

        if image is None:
            return "بدون تصویر"

        return format_html(
            '<img src="{}" '
            'width="100" '
            'height="100" '
            'style="'
            'object-fit:cover;'
            'border-radius:10px;'
            '" />',
            image.image.url,
        )

    # =====================================================
    # Actions
    # =====================================================

    @admin.action(
        description=(
            "محاسبه مجدد قیمت "
            "محصولات انتخاب‌شده"
        )
    )
    def recalculate_selected_prices(
        self,
        request,
        queryset,
    ):

        success_count = 0
        error_count = 0

        for product in queryset.iterator():

            try:

                recalculate_product_price(
                    product,
                    force=True,
                )

                success_count += 1

            except PricingError:

                error_count += 1

        self.message_user(
            request,
            (
                f"{success_count:,} محصول "
                f"بروزرسانی شد. "
                f"{error_count:,} خطا."
            ),
            level=(
                messages.SUCCESS
                if error_count == 0
                else messages.WARNING
            ),
        )

    @admin.action(
        description="افزودن به محصولات ویژه"
    )
    def mark_as_featured(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_featured=True
        )

    @admin.action(
        description="حذف از محصولات ویژه"
    )
    def remove_from_featured(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_featured=False
        )

    @admin.action(
        description="انتقال به آرشیو"
    )
    def archive_products(
        self,
        request,
        queryset,
    ):

        queryset.update(
            status=Product.Status.ARCHIVED
        )

    def save_model(
            self,
            request,
            obj,
            form,
            change,
    ):
        result = getattr(
            form,
            "_price_result",
            None,
        )

        if result is None:
            obj.current_price_toman = None
            obj.last_exchange_rate_toman = None
            obj.price_updated_at = None

        else:
            obj.current_price_toman = (
                result.final_price_toman
            )

            obj.last_exchange_rate_toman = (
                result.exchange_rate_toman
            )

            obj.price_updated_at = (
                timezone.now()
            )

        super().save_model(
            request,
            obj,
            form,
            change,
        )


# =========================================================
# Attribute Option Inline
# =========================================================


class ProductAttributeOptionInline(
    admin.TabularInline
):

    model = ProductAttributeOption

    extra = 1

    fields = (
        "value",
        "slug",
        "sort_order",
        "is_active",
    )

    readonly_fields = (
        "slug",
    )


# =========================================================
# Category Attribute Inline
# =========================================================


class CategoryAttributeInline(
    admin.TabularInline
):

    model = CategoryAttribute

    extra = 1

    autocomplete_fields = (
        "category",
    )

    fields = (
        "category",
        "is_required",
        "sort_order",
    )


# =========================================================
# Product Attribute Admin
# =========================================================


@admin.register(ProductAttribute)
class ProductAttributeAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "name",
        "data_type",
        "unit",
        "is_filterable",
        "is_searchable",
        "is_active",
        "sort_order",
    )

    list_filter = (
        "data_type",
        "is_filterable",
        "is_searchable",
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
    )

    ordering = (
        "sort_order",
        "name",
    )

    inlines = (
        ProductAttributeOptionInline,
        CategoryAttributeInline,
    )


# =========================================================
# Product Attribute Option Admin
# =========================================================


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "attribute",
        "value",
        "slug",
        "is_active",
        "sort_order",
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

    autocomplete_fields = (
        "attribute",
    )

    readonly_fields = (
        "slug",
    )