from rest_framework import serializers

from carts.models import Cart, CartItem

# =========================================================
# Cart Item Serializer
# =========================================================


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""

    variant_id = serializers.IntegerField(source="variant.id", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)
    variant_price = serializers.DecimalField(
        source="variant.price",
        max_digits=15,
        decimal_places=0,
        read_only=True,
    )
    variant_is_active = serializers.BooleanField(
        source="variant.is_active", read_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "cart",
            "variant",
            "variant_id",
            "variant_name",
            "variant_sku",
            "variant_price",
            "variant_is_active",
            "quantity",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "cart",
            "created_at",
            "updated_at",
        ]

    def get_total_price(self, obj):
        """Calculate total price for this cart item."""
        return int(obj.variant.price) * obj.quantity


# =========================================================
# Cart Serializer
# =========================================================


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "total_items",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

    def get_total_items(self, obj):
        """Get total number of items in cart."""
        return obj.items.count()

    def get_subtotal(self, obj):
        """Calculate subtotal for all items in cart."""
        total = 0
        for item in obj.items.all():
            total += int(item.variant.price) * item.quantity
        return total


# =========================================================
# Add to Cart Serializer
# =========================================================


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""

    variant_id = serializers.IntegerField(
        required=True,
        help_text="Product variant ID to add to cart.",
    )
    quantity = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        help_text="Quantity to add (default: 1).",
    )

    def validate_variant_id(self, value):
        """Validate that variant exists and is active."""
        from products.models import ProductVariant

        try:
            variant = ProductVariant.objects.select_related("product").get(pk=value)
            if not variant.is_active:
                raise serializers.ValidationError("این تنوع محصول غیرفعال است.")
            if variant.stock <= 0:
                raise serializers.ValidationError("این محصول موجودی ندارد.")
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("تنوع محصول یافت نشد.")
        return value

    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد.")
        return value


# =========================================================
# Update Cart Item Serializer
# =========================================================


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""

    quantity = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="New quantity for the cart item.",
    )

    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد.")
        return value
