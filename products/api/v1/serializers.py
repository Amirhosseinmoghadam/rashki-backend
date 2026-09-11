from django.db import transaction

from rest_framework import serializers

from brands.models import Brand
from categories.models import Category
from motorcycles.models import (
    MotorcycleBrand,
    MotorcycleModel,
)
from pricing.services import (
    PricingError,
    recalculate_product_price,
)

from products.models import (
    Product,
    ProductImage,
    ProductAttribute,
    ProductAttributeOption,
    CategoryAttribute,
    ProductAttributeValue,
    ProductCompatibility,
    ProductRelation,
)

from utils.normalizers import (
    normalize_single_line_text,
)
from drf_spectacular.utils import extend_schema_field

# =========================================================
# Helpers
# =========================================================


def get_category_tree_ids(
    category,
):

    """
    Category و تمام والدهای آن را
    از پایین به بالا برمی‌گرداند.
    """

    ids = []

    visited = set()

    current = category

    while current is not None:

        if current.pk in visited:
            break

        visited.add(
            current.pk
        )

        ids.append(
            current.pk
        )

        current = current.parent

    return ids


def is_category_tree_active(
    category,
):

    """
    Category تنها زمانی برای Product فعال محسوب
    می‌شود که خودش و تمام والدهایش Active باشند.
    """

    visited = set()

    current = category

    while current is not None:

        if current.pk in visited:
            return False

        visited.add(
            current.pk
        )

        if not current.is_active:
            return False

        current = current.parent

    return True


# =========================================================
# References
# =========================================================


class ProductCategoryReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Category

        fields = [
            "id",
            "name",
            "slug",
        ]

        read_only_fields = fields


class ProductBrandReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Brand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
        ]

        read_only_fields = fields


class ProductMotorcycleBrandReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = MotorcycleBrand

        fields = [
            "id",
            "name",
            "slug",
        ]

        read_only_fields = fields


class MotorcycleReferenceSerializer(
    serializers.ModelSerializer
):
    brand = (
        ProductMotorcycleBrandReferenceSerializer(
            read_only=True
        )
    )

    class Meta:

        model = MotorcycleModel

        fields = [
            "id",
            "brand",
            "name",
            "slug",
            "engine_volume",
            "production_start_year",
            "production_end_year",
        ]

        read_only_fields = fields


# =========================================================
# Product Image
# =========================================================


class ProductImageSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ProductImage

        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
            "sort_order",
        ]

        read_only_fields = [
            "id",
        ]


class ProductImageWriteSerializer(
    serializers.ModelSerializer
):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    class Meta:

        model = ProductImage

        fields = [
            "id",
            "product",
            "image",
            "alt_text",
            "is_primary",
            "sort_order",
        ]

        read_only_fields = [
            "id",
        ]

    def validate(
        self,
        attrs,
    ):

        product = attrs.get(
            "product"
        )

        if self.instance:

            current_product = (
                self.instance.product
            )

            product = (
                product
                or current_product
            )

            if (
                product.pk
                != current_product.pk
            ):

                raise serializers.ValidationError(
                    {
                        "product": (
                            "انتقال تصویر از یک "
                            "محصول به محصول دیگر "
                            "مجاز نیست."
                        )
                    }
                )

        if (
            self.instance is None
            and ProductImage.objects.filter(
                product=product
            ).count()
            >= ProductImage.MAX_IMAGES_PER_PRODUCT
        ):

            raise serializers.ValidationError(
                {
                    "image": (
                        "برای هر محصول حداکثر "
                        "20 تصویر قابل ثبت است."
                    )
                }
            )

        return attrs


# =========================================================
# Attribute
# =========================================================


class ProductAttributeOptionSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ProductAttributeOption

        fields = [
            "id",
            "value",
            "slug",
            "sort_order",
        ]

        read_only_fields = fields


class ProductAttributeReferenceSerializer(
    serializers.ModelSerializer
):

    options = (
        ProductAttributeOptionSerializer(
            many=True,
            read_only=True,
        )
    )

    class Meta:

        model = ProductAttribute

        fields = [
            "id",
            "name",
            "slug",
            "data_type",
            "unit",
            "is_filterable",
            "is_searchable",
            "sort_order",
            "options",
        ]

        read_only_fields = fields


class ProductAttributeValueSerializer(
    serializers.ModelSerializer
):

    attribute = (
        ProductAttributeReferenceSerializer(
            read_only=True
        )
    )

    option = (
        ProductAttributeOptionSerializer(
            read_only=True
        )
    )

    class Meta:

        model = ProductAttributeValue

        fields = [
            "id",
            "attribute",
            "value_text",
            "value_number",
            "value_boolean",
            "option",
        ]

        read_only_fields = fields


# =========================================================
# Attribute Write
# =========================================================


class ProductAttributeValueWriteSerializer(
    serializers.Serializer
):

    attribute = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                ProductAttribute.objects
                .filter(
                    is_active=True
                )
            )
        )
    )

    value_text = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    value_number = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        required=False,
        allow_null=True,
    )

    value_boolean = serializers.BooleanField(
        required=False,
        allow_null=True,
    )

    option = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                ProductAttributeOption.objects
                .filter(
                    is_active=True
                )
            ),
            required=False,
            allow_null=True,
        )
    )

    def validate(
        self,
        attrs,
    ):

        attribute = attrs[
            "attribute"
        ]

        value_text = attrs.get(
            "value_text",
            ""
        )

        value_number = attrs.get(
            "value_number"
        )

        value_boolean = attrs.get(
            "value_boolean"
        )

        option = attrs.get(
            "option"
        )

        data_type = (
            attribute.data_type
        )

        if (
            data_type
            == ProductAttribute.DataType.TEXT
        ):

            if not value_text.strip():

                raise serializers.ValidationError(
                    {
                        "value_text": (
                            "مقدار متنی الزامی است."
                        )
                    }
                )

        elif (
            data_type
            == ProductAttribute.DataType.NUMBER
        ):

            if value_number is None:

                raise serializers.ValidationError(
                    {
                        "value_number": (
                            "مقدار عددی الزامی است."
                        )
                    }
                )

        elif (
            data_type
            == ProductAttribute.DataType.BOOLEAN
        ):

            if value_boolean is None:

                raise serializers.ValidationError(
                    {
                        "value_boolean": (
                            "انتخاب بله یا خیر "
                            "الزامی است."
                        )
                    }
                )

        elif (
            data_type
            == ProductAttribute.DataType.CHOICE
        ):

            if option is None:

                raise serializers.ValidationError(
                    {
                        "option": (
                            "انتخاب یک گزینه "
                            "الزامی است."
                        )
                    }
                )

            if (
                option.attribute_id
                != attribute.id
            ):

                raise serializers.ValidationError(
                    {
                        "option": (
                            "گزینه انتخاب‌شده "
                            "متعلق به این ویژگی نیست."
                        )
                    }
                )

        return attrs


# =========================================================
# Compatibility
# =========================================================


class ProductCompatibilitySerializer(
    serializers.ModelSerializer
):

    motorcycle = (
        MotorcycleReferenceSerializer(
            read_only=True
        )
    )

    class Meta:

        model = ProductCompatibility

        fields = [
            "id",
            "motorcycle",
            "compatible_start_year",
            "compatible_end_year",
            "note",
        ]

        read_only_fields = fields


class ProductCompatibilityWriteSerializer(
    serializers.Serializer
):

    motorcycle = (
        serializers.PrimaryKeyRelatedField(
            queryset=(
                MotorcycleModel.objects.all()
            )
        )
    )

    compatible_start_year = (
        serializers.IntegerField(
            required=False,
            allow_null=True,
            min_value=1,
        )
    )

    compatible_end_year = (
        serializers.IntegerField(
            required=False,
            allow_null=True,
            min_value=1,
        )
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )

    def validate(
        self,
        attrs,
    ):

        motorcycle = attrs[
            "motorcycle"
        ]

        start = attrs.get(
            "compatible_start_year"
        )

        end = attrs.get(
            "compatible_end_year"
        )

        if (
            start is not None
            and end is not None
            and end < start
        ):

            raise serializers.ValidationError(
                {
                    "compatible_end_year": (
                        "سال پایان سازگاری "
                        "نمی‌تواند قبل از "
                        "سال شروع باشد."
                    )
                }
            )

        if (
            start is not None
            and motorcycle.production_start_year
            is not None
            and start
            < motorcycle.production_start_year
        ):

            raise serializers.ValidationError(
                {
                    "compatible_start_year": (
                        "سال شروع سازگاری "
                        "قبل از شروع تولید "
                        "این مدل موتورسیکلت است."
                    )
                }
            )

        if (
            end is not None
            and motorcycle.production_end_year
            is not None
            and end
            > motorcycle.production_end_year
        ):

            raise serializers.ValidationError(
                {
                    "compatible_end_year": (
                        "سال پایان سازگاری "
                        "بعد از پایان تولید "
                        "این مدل موتورسیکلت است."
                    )
                }
            )

        return attrs


# =========================================================
# Related Product Preview
# =========================================================


class RelatedProductSerializer(
    serializers.ModelSerializer
):

    primary_image = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "current_price_toman",
            "primary_image",
        ]

        read_only_fields = fields

    @extend_schema_field(
        serializers.URLField(
            allow_null=True
        )
    )
    def get_primary_image(self, obj):

        image = next(
            (
                image
                for image in obj.images.all()
                if image.is_primary
            ),
            None,
        )

        if image is None:
            return None

        request = self.context.get(
            "request"
        )

        url = image.image.url

        if request:
            return request.build_absolute_uri(
                url
            )

        return url


# =========================================================
# Product List
# =========================================================


class ProductListSerializer(
    serializers.ModelSerializer
):

    category = (
        ProductCategoryReferenceSerializer(
            read_only=True
        )
    )

    brand = (
        ProductBrandReferenceSerializer(
            read_only=True
        )
    )

    primary_image = (
        serializers.SerializerMethodField()
    )

    is_in_stock = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "sku",
            "category",
            "brand",
            "short_description",
            "current_price_toman",
            "unit",
            "stock_quantity",
            "is_in_stock",
            "is_featured",
            "primary_image",
        ]

        read_only_fields = fields

    @extend_schema_field(
        serializers.URLField(
            allow_null=True
        )
    )
    def get_primary_image(self, obj):

        image = next(
            (
                image
                for image in obj.images.all()
                if image.is_primary
            ),
            None,
        )

        if image is None:
            return None

        request = self.context.get(
            "request"
        )

        url = image.image.url

        if request:
            return request.build_absolute_uri(
                url
            )

        return url

    @extend_schema_field(
        serializers.BooleanField()
    )
    def get_is_in_stock(self, obj):

        return obj.stock_quantity > 0


# =========================================================
# Product Detail
# =========================================================


class ProductDetailSerializer(
    serializers.ModelSerializer
):

    category = (
        ProductCategoryReferenceSerializer(
            read_only=True
        )
    )

    brand = (
        ProductBrandReferenceSerializer(
            read_only=True
        )
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )

    attributes = (
        ProductAttributeValueSerializer(
            source="attribute_values",
            many=True,
            read_only=True,
        )
    )

    compatibilities = (
        ProductCompatibilitySerializer(
            many=True,
            read_only=True,
        )
    )

    related_products = (
        serializers.SerializerMethodField()
    )

    is_in_stock = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "category",
            "brand",
            "unit",
            "sku",
            "manufacturer_part_number",
            "oem_code",
            "barcode",
            "short_description",
            "description",
            "current_price_toman",
            "stock_quantity",
            "is_in_stock",
            "weight_grams",
            "length_cm",
            "width_cm",
            "height_cm",
            "images",
            "attributes",
            "compatibilities",
            "related_products",
            "meta_title",
            "meta_description",
            "is_featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

    @extend_schema_field(
        serializers.BooleanField()
    )
    def get_is_in_stock(self, obj):
        return obj.stock_quantity > 0

    @extend_schema_field(
        RelatedProductSerializer(
            many=True
        )
    )
    def get_related_products(
            self,
            obj,
    ):
        products = [
            relation.related_product
            for relation in obj.relations.all()
            if (
                    relation.related_product.status
                    == Product.Status.ACTIVE
            )
        ]

        return RelatedProductSerializer(
            products,
            many=True,
            context=self.context,
        ).data


# =========================================================
# Product Write
# =========================================================


class ProductCreateUpdateSerializer(
    serializers.ModelSerializer
):

    slug = serializers.CharField(
        read_only=True,
    )

    current_price_toman = (
        serializers.IntegerField(
            read_only=True
        )
    )

    category = (
        serializers.PrimaryKeyRelatedField(
            queryset=Category.objects.all()
        )
    )

    brand = (
        serializers.PrimaryKeyRelatedField(
            queryset=Brand.objects.all(),
            required=False,
            allow_null=True,
        )
    )

    attributes = (
        ProductAttributeValueWriteSerializer(
            many=True,
            required=False,
            write_only=True,
        )
    )

    compatibilities = (
        ProductCompatibilityWriteSerializer(
            many=True,
            required=False,
            write_only=True,
        )
    )

    related_product_ids = (
        serializers.PrimaryKeyRelatedField(
            queryset=Product.objects.all(),
            many=True,
            required=False,
            write_only=True,
        )
    )

    class Meta:

        model = Product

        fields = [
            "name",
            "slug",
            "category",
            "brand",
            "unit",
            "sku",
            "manufacturer_part_number",
            "oem_code",
            "barcode",
            "short_description",
            "description",
            "search_keywords",
            "pricing_mode",
            "base_price_usd",
            "base_price_toman",
            "markup_percent",
            "fixed_cost_toman",
            "current_price_toman",
            "is_price_locked",
            "stock_quantity",
            "low_stock_threshold",
            "weight_grams",
            "length_cm",
            "width_cm",
            "height_cm",
            "meta_title",
            "meta_description",
            "status",
            "is_featured",
            "attributes",
            "compatibilities",
            "related_product_ids",
        ]

        read_only_fields = [
            "slug",
            "current_price_toman",
        ]

    # =====================================================
    # Name
    # =====================================================

    def validate_name(
        self,
        value,
    ):

        value = (
            normalize_single_line_text(
                value
            )
        )

        if not value:

            raise serializers.ValidationError(
                "نام محصول الزامی است."
            )

        return value

    # =====================================================
    # Main Validation
    # =====================================================

    def validate(
        self,
        attrs,
    ):

        instance = self.instance

        category = attrs.get(
            "category",
            (
                instance.category
                if instance
                else None
            ),
        )

        brand = attrs.get(
            "brand",
            (
                instance.brand
                if instance
                else None
            ),
        )

        status_value = attrs.get(
            "status",
            (
                instance.status
                if instance
                else Product.Status.DRAFT
            ),
        )

        pricing_mode = attrs.get(
            "pricing_mode",
            (
                instance.pricing_mode
                if instance
                else Product.PricingMode.FIXED
            ),
        )

        base_price_usd = attrs.get(
            "base_price_usd",
            (
                instance.base_price_usd
                if instance
                else None
            ),
        )

        base_price_toman = attrs.get(
            "base_price_toman",
            (
                instance.base_price_toman
                if instance
                else None
            ),
        )

        # -------------------------------------------------
        # Pricing
        # -------------------------------------------------

        if (
            pricing_mode
            == Product.PricingMode.USD_BASED
            and base_price_usd is None
        ):

            raise serializers.ValidationError(
                {
                    "base_price_usd": (
                        "برای قیمت‌گذاری دلاری "
                        "قیمت پایه دلار الزامی است."
                    )
                }
            )

        if (
            pricing_mode
            == Product.PricingMode.FIXED
            and base_price_toman is None
        ):

            raise serializers.ValidationError(
                {
                    "base_price_toman": (
                        "برای قیمت‌گذاری ثابت "
                        "قیمت پایه تومان الزامی است."
                    )
                }
            )

        # -------------------------------------------------
        # Active Product
        # -------------------------------------------------

        if (
            status_value
            == Product.Status.ACTIVE
        ):

            if not is_category_tree_active(
                category
            ):

                raise serializers.ValidationError(
                    {
                        "category": (
                            "محصول فعال باید در "
                            "دسته‌بندی فعال قرار گیرد "
                            "و تمام والدهای دسته‌بندی "
                            "نیز فعال باشند."
                        )
                    }
                )

            if (
                brand is not None
                and not brand.is_active
            ):

                raise serializers.ValidationError(
                    {
                        "brand": (
                            "برند محصول فعال "
                            "نمی‌تواند غیرفعال باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # Attributes
        # -------------------------------------------------

        attribute_items = attrs.get(
            "attributes"
        )

        if attribute_items is not None:

            attribute_ids = [
                item["attribute"].id
                for item in attribute_items
            ]

            if (
                len(attribute_ids)
                != len(set(attribute_ids))
            ):

                raise serializers.ValidationError(
                    {
                        "attributes": (
                            "هر ویژگی فقط یک بار "
                            "قابل ارسال است."
                        )
                    }
                )

            category_ids = (
                get_category_tree_ids(
                    category
                )
            )

            allowed_ids = set(
                CategoryAttribute.objects
                .filter(
                    category_id__in=(
                        category_ids
                    )
                )
                .values_list(
                    "attribute_id",
                    flat=True,
                )
            )

            invalid_ids = (
                set(attribute_ids)
                - allowed_ids
            )

            if invalid_ids:

                raise serializers.ValidationError(
                    {
                        "attributes": (
                            "یک یا چند ویژگی "
                            "برای دسته‌بندی این "
                            "محصول تعریف نشده‌اند."
                        )
                    }
                )

        # -------------------------------------------------
        # Required Attributes
        # -------------------------------------------------

        if category:

            category_ids = (
                get_category_tree_ids(
                    category
                )
            )

            required_ids = set(
                CategoryAttribute.objects
                .filter(
                    category_id__in=(
                        category_ids
                    ),
                    is_required=True,
                )
                .values_list(
                    "attribute_id",
                    flat=True,
                )
            )

            if attribute_items is not None:

                final_attribute_ids = {
                    item["attribute"].id
                    for item
                    in attribute_items
                }

            elif instance:

                final_attribute_ids = set(
                    instance.attribute_values
                    .values_list(
                        "attribute_id",
                        flat=True,
                    )
                )

            else:

                final_attribute_ids = set()

            missing = (
                required_ids
                - final_attribute_ids
            )

            if missing:

                raise serializers.ValidationError(
                    {
                        "attributes": (
                            "برخی ویژگی‌های الزامی "
                            "این دسته‌بندی وارد "
                            "نشده‌اند."
                        )
                    }
                )

        # -------------------------------------------------
        # Compatibility Duplicates
        # -------------------------------------------------

        compatibilities = attrs.get(
            "compatibilities"
        )

        if compatibilities is not None:

            motorcycle_ids = [
                item["motorcycle"].id
                for item in compatibilities
            ]

            if (
                len(motorcycle_ids)
                != len(set(motorcycle_ids))
            ):

                raise serializers.ValidationError(
                    {
                        "compatibilities": (
                            "یک مدل موتورسیکلت "
                            "بیش از یک بار ارسال شده است."
                        )
                    }
                )

        return attrs

    # =====================================================
    # Sync Attributes
    # =====================================================

    def _sync_attributes(
        self,
        product,
        items,
    ):

        attribute_ids = [
            item["attribute"].id
            for item in items
        ]

        ProductAttributeValue.objects.filter(
            product=product
        ).exclude(
            attribute_id__in=attribute_ids
        ).delete()

        for item in items:

            ProductAttributeValue.objects.update_or_create(
                product=product,
                attribute=item[
                    "attribute"
                ],
                defaults={
                    "value_text": item.get(
                        "value_text",
                        "",
                    ),
                    "value_number": item.get(
                        "value_number"
                    ),
                    "value_boolean": item.get(
                        "value_boolean"
                    ),
                    "option": item.get(
                        "option"
                    ),
                },
            )

    # =====================================================
    # Sync Compatibility
    # =====================================================

    def _sync_compatibilities(
        self,
        product,
        items,
    ):

        motorcycle_ids = [
            item["motorcycle"].id
            for item in items
        ]

        ProductCompatibility.objects.filter(
            product=product
        ).exclude(
            motorcycle_id__in=(
                motorcycle_ids
            )
        ).delete()

        for item in items:

            ProductCompatibility.objects.update_or_create(
                product=product,
                motorcycle=item[
                    "motorcycle"
                ],
                defaults={
                    "compatible_start_year": (
                        item.get(
                            "compatible_start_year"
                        )
                    ),
                    "compatible_end_year": (
                        item.get(
                            "compatible_end_year"
                        )
                    ),
                    "note": item.get(
                        "note",
                        "",
                    ),
                },
            )

    # =====================================================
    # Sync Related Products
    # =====================================================

    def _sync_related_products(
        self,
        product,
        products,
    ):

        ids = [
            related.id
            for related in products
            if related.id != product.id
        ]

        ProductRelation.objects.filter(
            product=product
        ).exclude(
            related_product_id__in=ids
        ).delete()

        for sort_order, related in enumerate(
            products
        ):

            if related.pk == product.pk:
                continue

            ProductRelation.objects.update_or_create(
                product=product,
                related_product=related,
                defaults={
                    "sort_order": sort_order,
                },
            )

    # =====================================================
    # Save Product
    # =====================================================

    def _save_product(
        self,
        product,
        attributes,
        compatibilities,
        related_products,
    ):

        # قیمت Product بعد از ذخیره
        # دوباره محاسبه می‌شود.
        try:

            recalculate_product_price(
                product,
                force=True,
            )

        except PricingError as exc:

            # Draft می‌تواند در صورت نبود نرخ دلار
            # فعلاً بدون قیمت نهایی ذخیره شود.
            if (
                product.status
                == Product.Status.ACTIVE
            ):

                raise serializers.ValidationError(
                    {
                        "pricing": str(exc)
                    }
                )

        if attributes is not None:

            self._sync_attributes(
                product,
                attributes,
            )

        if compatibilities is not None:

            self._sync_compatibilities(
                product,
                compatibilities,
            )

        if related_products is not None:

            self._sync_related_products(
                product,
                related_products,
            )

        return product

    # =====================================================
    # Create
    # =====================================================

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):

        attributes = validated_data.pop(
            "attributes",
            None,
        )

        compatibilities = validated_data.pop(
            "compatibilities",
            None,
        )

        related_products = validated_data.pop(
            "related_product_ids",
            None,
        )

        product = Product.objects.create(
            **validated_data
        )

        return self._save_product(
            product,
            attributes,
            compatibilities,
            related_products,
        )

    # =====================================================
    # Update
    # =====================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):

        attributes = validated_data.pop(
            "attributes",
            None,
        )

        compatibilities = validated_data.pop(
            "compatibilities",
            None,
        )

        related_products = validated_data.pop(
            "related_product_ids",
            None,
        )

        for field, value in (
            validated_data.items()
        ):

            setattr(
                instance,
                field,
                value,
            )

        instance.save()

        return self._save_product(
            instance,
            attributes,
            compatibilities,
            related_products,
        )