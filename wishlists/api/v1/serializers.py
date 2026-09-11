from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema_field,
)

from brands.models import Brand
from categories.models import Category

from products.models import Product

from wishlists.models import WishlistItem


# =========================================================
# Category Reference
# =========================================================


class WishlistCategorySerializer(
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


# =========================================================
# Brand Reference
# =========================================================


class WishlistBrandSerializer(
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
# Wishlist Product
# =========================================================


class WishlistProductSerializer(
    serializers.ModelSerializer
):

    category = (
        WishlistCategorySerializer(
            read_only=True
        )
    )

    brand = (
        WishlistBrandSerializer(
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
            "primary_image",
        ]

        read_only_fields = fields

    # =====================================================
    # Primary Image
    # =====================================================

    @extend_schema_field(
        serializers.URLField(
            allow_null=True
        )
    )
    def get_primary_image(
        self,
        obj,
    ):

        # در selector فقط Primary Image
        # Prefetch شده است.
        images = getattr(
            obj,
            "_wishlist_primary_images",
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

    # =====================================================
    # Stock
    # =====================================================

    @extend_schema_field(
        serializers.BooleanField()
    )
    def get_is_in_stock(
        self,
        obj,
    ):

        return (
            obj.stock_quantity > 0
        )


# =========================================================
# Wishlist Item
# =========================================================


class WishlistItemSerializer(
    serializers.ModelSerializer
):

    product = (
        WishlistProductSerializer(
            read_only=True
        )
    )

    class Meta:

        model = WishlistItem

        fields = [
            "id",
            "product",
            "created_at",
        ]

        read_only_fields = fields