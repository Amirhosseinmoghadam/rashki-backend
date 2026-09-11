from rest_framework import serializers

from orders.models import (
    Order,
    OrderItem,
)


# =========================================================
# Create
# =========================================================


class OrderCreateSerializer(
    serializers.Serializer
):

    # آدرس ذخیره‌شده User.
    address_id = serializers.IntegerField(
        min_value=1,
    )

    # ShippingMethod انتخاب‌شده.
    shipping_method_id = (
        serializers.IntegerField(
            min_value=1,
        )
    )

    # پذیرش قوانین Checkout.
    accept_terms = (
        serializers.BooleanField()
    )

    # توضیح اختیاری مشتری.
    customer_note = (
        serializers.CharField(
            max_length=1000,
            required=False,
            allow_blank=True,
        )
    )

    def validate_accept_terms(
        self,
        value,
    ):

        if value is not True:

            raise serializers.ValidationError(
                "پذیرش قوانین الزامی است."
            )

        return value


# =========================================================
# Order Item
# =========================================================


class OrderItemSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = OrderItem

        fields = [
            "id",
            "product_id_snapshot",
            "product_name",
            "product_slug",
            "product_sku",
            "product_brand_name",
            "product_unit",
            "unit_price_toman",
            "quantity",
            "total_price_toman",
        ]

        read_only_fields = fields


# =========================================================
# List
# =========================================================


class OrderListSerializer(
    serializers.ModelSerializer
):

    item_count = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = Order

        fields = [
            "order_number",
            "status",
            "payment_status",
            "item_count",
            "subtotal_toman",
            "discount_amount_toman",
            "shipping_amount_toman",
            "total_toman",
            "shipping_method_name",
            "expires_at",
            "paid_at",
            "created_at",
        ]

        read_only_fields = fields

    def get_item_count(
        self,
        obj,
    ) -> int:

        return sum(
            item.quantity
            for item
            in obj.items.all()
        )


# =========================================================
# Detail
# =========================================================


class OrderDetailSerializer(
    serializers.ModelSerializer
):

    items = OrderItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:

        model = Order

        fields = [
            "order_number",
            "status",
            "payment_status",

            # Items
            "items",

            # Amounts
            "subtotal_toman",
            "eligible_discount_subtotal_toman",
            "discount_amount_toman",
            "shipping_amount_toman",
            "total_toman",

            # Discount
            "discount_code",
            "discount_type",
            "discount_scope",

            # Shipping
            "shipping_method_code",
            "shipping_method_name",
            "shipping_provider",
            "shipping_service_code",
            "shipping_weight_grams",

            # Address Snapshot
            "shipping_first_name",
            "shipping_last_name",
            "shipping_mobile_number",
            "shipping_phone_number",
            "shipping_province_name",
            "shipping_city_name",
            "shipping_postal_code",
            "shipping_postal_address",

            "customer_note",

            # Dates
            "terms_accepted_at",
            "expires_at",
            "paid_at",
            "cancelled_at",
            "shipped_at",
            "delivered_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields

# =========================================================
# Order Cancellation
# =========================================================


class OrderCancellationRequestSerializer(
    serializers.Serializer
):

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        default="customer_request",
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        default="",
    )


class OrderCancellationResultSerializer(
    serializers.Serializer
):

    order_number = serializers.CharField()

    order_status = serializers.CharField()

    payment_status = serializers.CharField()

    already_cancelled = serializers.BooleanField()

    shipment_id = serializers.IntegerField(
        allow_null=True,
    )

    shipment_status = serializers.CharField(
        allow_null=True,
    )

    refund_public_id = serializers.UUIDField(
        allow_null=True,
    )

    refund_status = serializers.CharField(
        allow_null=True,
    )