from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema_field,
)

from brands.models import Brand
from categories.models import Category
from products.models import Product

from carts.constants import (
    MAX_CART_ITEM_QUANTITY,
)


# =========================================================
# Product References
# =========================================================


class CartCategorySerializer(
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


class CartBrandSerializer(
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


# =========================================================
# Product
# =========================================================


class CartProductSerializer(
    serializers.ModelSerializer
):

    category = CartCategorySerializer(
        read_only=True
    )

    brand = CartBrandSerializer(
        read_only=True
    )

    primary_image = (
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
            "unit",
            "primary_image",
        ]

        read_only_fields = fields

    @extend_schema_field(
        serializers.URLField(
            allow_null=True
        )
    )
    def get_primary_image(
        self,
        obj,
    ):

        images = getattr(
            obj,
            "_cart_primary_images",
            None,
        )

        if images is not None:

            image = (
                images[0]
                if images
                else None
            )

        else:

            image = (
                obj.images
                .filter(
                    is_primary=True
                )
                .first()
            )

        if image is None:
            return None

        url = image.image.url

        request = self.context.get(
            "request"
        )

        if request:

            return (
                request
                .build_absolute_uri(url)
            )

        return url


# =========================================================
# Cart Item Output
# =========================================================


class CartItemSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField()

    product = CartProductSerializer()

    quantity = serializers.IntegerField()

    unit_price_toman = (
        serializers.IntegerField(
            allow_null=True
        )
    )

    line_total_toman = (
        serializers.IntegerField(
            allow_null=True
        )
    )

    is_available = (
        serializers.BooleanField()
    )

    availability_message = (
        serializers.CharField(
            allow_null=True
        )
    )

    available_stock = (
        serializers.IntegerField()
    )

    created_at = (
        serializers.DateTimeField()
    )

    updated_at = (
        serializers.DateTimeField()
    )


# =========================================================
# Discount Output
# =========================================================


class CartDiscountSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField()

    code = serializers.CharField()

    discount_type = serializers.CharField()

    scope = serializers.CharField()

    eligible_subtotal_toman = (
        serializers.IntegerField(
            required=False
        )
    )

    discount_amount_toman = (
        serializers.IntegerField(
            required=False
        )
    )


# =========================================================
# Cart Output
# =========================================================


class CartSerializer(
    serializers.Serializer
):

    id = serializers.IntegerField()

    items = CartItemSerializer(
        many=True
    )

    item_count = (
        serializers.IntegerField()
    )

    total_quantity = (
        serializers.IntegerField()
    )

    subtotal_toman = (
        serializers.IntegerField()
    )

    applied_discount = (
        CartDiscountSerializer(
            allow_null=True
        )
    )

    discount_valid = (
        serializers.BooleanField(
            allow_null=True
        )
    )

    discount_error = (
        serializers.CharField(
            allow_null=True
        )
    )

    discount_amount_toman = (
        serializers.IntegerField()
    )

    final_subtotal_toman = (
        serializers.IntegerField()
    )

    has_issues = (
        serializers.BooleanField()
    )

    is_checkout_ready = (
        serializers.BooleanField()
    )

    created_at = (
        serializers.DateTimeField()
    )

    updated_at = (
        serializers.DateTimeField()
    )


# =========================================================
# Add Item Request
# =========================================================


class CartItemAddSerializer(
    serializers.Serializer
):

    product_id = serializers.IntegerField(
        min_value=1,
    )

    # در POST اگر Product از قبل داخل Cart باشد،
    # این Quantity به مقدار قبلی اضافه می‌شود.
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=(
            MAX_CART_ITEM_QUANTITY
        ),
        default=1,
    )


# =========================================================
# Update Quantity Request
# =========================================================


class CartItemUpdateSerializer(
    serializers.Serializer
):

    # در PATCH مقدار Quantity
    # جایگزین Quantity قبلی می‌شود.
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=(
            MAX_CART_ITEM_QUANTITY
        ),
    )


# =========================================================
# Discount Request
# =========================================================


class CartDiscountApplySerializer(
    serializers.Serializer
):

    code = serializers.CharField(
        max_length=50,
    )