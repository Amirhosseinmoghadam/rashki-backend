from rest_framework import serializers

from products.models import (
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
# Product Image Serializers
# =========================================================


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product",
            "image",
            "alt_text",
            "caption",
            "is_primary",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ProductImage."""

    class Meta:
        model = ProductImage
        fields = [
            "product",
            "image",
            "alt_text",
            "caption",
            "is_primary",
            "sort_order",
        ]


# =========================================================
# Attribute Group Serializers
# =========================================================


class AttributeGroupSerializer(serializers.ModelSerializer):
    """Serializer for AttributeGroup model."""

    class Meta:
        model = AttributeGroup
        fields = [
            "id",
            "name",
            "slug",
            "sort_order",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]


class AttributeGroupCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating AttributeGroup."""

    class Meta:
        model = AttributeGroup
        fields = [
            "name",
            "sort_order",
            "is_active",
        ]


# =========================================================
# Attribute Serializers
# =========================================================


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer for Attribute model."""

    group_name = serializers.CharField(
        source="group.name",
        read_only=True,
    )
    value_type_display = serializers.CharField(
        source="get_value_type_display",
        read_only=True,
    )

    class Meta:
        model = Attribute
        fields = [
            "id",
            "group",
            "group_name",
            "name",
            "slug",
            "value_type",
            "value_type_display",
            "unit",
            "is_filterable",
            "is_required",
            "sort_order",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]


class AttributeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Attribute."""

    class Meta:
        model = Attribute
        fields = [
            "group",
            "name",
            "value_type",
            "unit",
            "is_filterable",
            "is_required",
            "sort_order",
            "is_active",
        ]


# =========================================================
# Attribute Value Serializers
# =========================================================


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for AttributeValue model."""

    attribute_name = serializers.CharField(
        source="attribute.name",
        read_only=True,
    )

    class Meta:
        model = AttributeValue
        fields = [
            "id",
            "attribute",
            "attribute_name",
            "value",
            "slug",
            "sort_order",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]


class AttributeValueCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating AttributeValue."""

    class Meta:
        model = AttributeValue
        fields = [
            "attribute",
            "value",
            "sort_order",
            "is_active",
        ]


# =========================================================
# Product Attribute Value Serializers
# =========================================================


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for ProductAttributeValue model."""

    attribute_name = serializers.CharField(
        source="attribute.name",
        read_only=True,
    )
    attribute_slug = serializers.CharField(
        source="attribute.slug",
        read_only=True,
    )

    class Meta:
        model = ProductAttributeValue
        fields = [
            "id",
            "product",
            "attribute",
            "attribute_name",
            "attribute_slug",
            "value",
        ]
        read_only_fields = ["id"]


class ProductAttributeValueCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ProductAttributeValue."""

    class Meta:
        model = ProductAttributeValue
        fields = [
            "product",
            "attribute",
            "value",
        ]


# =========================================================
# Variant Attribute Value Serializers
# =========================================================


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for VariantAttributeValue model."""

    attribute_name = serializers.CharField(
        source="attribute.name",
        read_only=True,
    )
    value_value = serializers.CharField(
        source="value.value",
        read_only=True,
    )

    class Meta:
        model = VariantAttributeValue
        fields = [
            "id",
            "variant",
            "attribute",
            "attribute_name",
            "value",
            "value_value",
        ]
        read_only_fields = ["id"]


class VariantAttributeValueCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating VariantAttributeValue."""

    class Meta:
        model = VariantAttributeValue
        fields = [
            "variant",
            "attribute",
            "value",
        ]


# =========================================================
# Product Variant Serializers
# =========================================================


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model."""

    is_in_stock = serializers.BooleanField(
        read_only=True,
    )
    is_available = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product",
            "name",
            "sku",
            "price",
            "stock",
            "is_active",
            "is_in_stock",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_in_stock",
            "is_available",
            "created_at",
            "updated_at",
        ]


class ProductVariantCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ProductVariant."""

    class Meta:
        model = ProductVariant
        fields = [
            "product",
            "name",
            "sku",
            "price",
            "stock",
            "is_active",
        ]


class ProductVariantDetailSerializer(ProductVariantSerializer):
    """Detailed serializer for ProductVariant with nested attributes."""

    attribute_values = VariantAttributeValueSerializer(
        many=True,
        read_only=True,
    )

    class Meta(ProductVariantSerializer.Meta):
        fields = ProductVariantSerializer.Meta.fields + ["attribute_values"]


# =========================================================
# Product Motorcycle Compatibility Serializers
# =========================================================


class ProductMotorcycleCompatibilitySerializer(serializers.ModelSerializer):
    """Serializer for ProductMotorcycleCompatibility model."""

    motorcycle_name = serializers.CharField(
        source="motorcycle.name",
        read_only=True,
    )

    class Meta:
        model = ProductMotorcycleCompatibility
        fields = [
            "id",
            "product",
            "motorcycle",
            "motorcycle_name",
            "note",
        ]
        read_only_fields = ["id"]


class ProductMotorcycleCompatibilityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ProductMotorcycleCompatibility."""

    class Meta:
        model = ProductMotorcycleCompatibility
        fields = [
            "product",
            "motorcycle",
            "note",
        ]


# =========================================================
# Product Serializers
# =========================================================


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products."""

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    primary_image = serializers.SerializerMethodField()
    variants_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "brand_name",
            "category",
            "category_name",
            "short_description",
            "is_active",
            "is_featured",
            "created_at",
            "primary_image",
            "variants_count",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return {
                "id": primary_image.id,
                "image_url": primary_image.image.url if primary_image.image else None,
                "alt_text": primary_image.alt_text,
            }
        return None

    def get_variants_count(self, obj):
        return obj.variants.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Product model."""

    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )
    attribute_values = ProductAttributeValueSerializer(
        many=True,
        read_only=True,
    )
    variants = ProductVariantSerializer(
        many=True,
        read_only=True,
    )
    motorcycle_compatibilities = ProductMotorcycleCompatibilitySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "brand",
            "brand_name",
            "category",
            "category_name",
            "short_description",
            "description",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
            "images",
            "attribute_values",
            "variants",
            "motorcycle_compatibilities",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Product."""

    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "category",
            "short_description",
            "description",
            "is_active",
            "is_featured",
        ]
