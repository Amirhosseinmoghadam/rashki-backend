from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from carts.api.v1.serializers import (
    CartSerializer,
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    CartDiscountApplySerializer,
)

from . import examples
from . import responses


# =========================================================
# Response
# =========================================================


CartResponseSerializer = inline_serializer(
    name="CartResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": CartSerializer(),
    },
)


CartErrorResponseSerializer = inline_serializer(
    name="CartErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True
        ),
    },
)


# =========================================================
# Cart Detail
# =========================================================


cart_detail_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_detail",
    summary="Get Cart",
    description=(
        "Returns the authenticated user's cart. "
        "Prices and stock are evaluated using current "
        "backend values. Shipping is not included yet."
    ),
    responses={
        200: OpenApiResponse(
            response=CartResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Cart",
                    value=responses.CartSuccess,
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Authentication Required",
                    value=(
                        responses
                        .AuthenticationRequired
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Add Item
# =========================================================


cart_add_item_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_item_add",
    summary="Add Product To Cart",
    description=(
        "Adds a product to the cart. "
        "If the product already exists in the cart, "
        "the submitted quantity is added to the "
        "existing quantity."
    ),
    request=CartItemAddSerializer,
    examples=[
        OpenApiExample(
            name="Add Product",
            value=(
                examples
                .CART_ADD_ITEM_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        201: CartResponseSerializer,
        200: CartResponseSerializer,
        400: OpenApiResponse(
            response=CartErrorResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Unavailable Product",
                    value=(
                        responses
                        .CartProductUnavailable
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Insufficient Stock",
                    value=(
                        responses
                        .CartStockError
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Update Item
# =========================================================


cart_update_item_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_item_update",
    summary="Update Cart Item Quantity",
    description=(
        "Sets the absolute quantity of a product "
        "already present in the cart."
    ),
    request=CartItemUpdateSerializer,
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        )
    ],
    examples=[
        OpenApiExample(
            name="Update Quantity",
            value=(
                examples
                .CART_UPDATE_ITEM_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        200: CartResponseSerializer,
        400: CartErrorResponseSerializer,
        401: OpenApiTypes.OBJECT,
        404: OpenApiResponse(
            response=CartErrorResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Not In Cart",
                    value=(
                        responses
                        .CartItemNotFound
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Remove Item
# =========================================================


cart_remove_item_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_item_remove",
    summary="Remove Product From Cart",
    request=None,
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            required=True,
        )
    ],
    responses={
        200: CartResponseSerializer,
        401: OpenApiTypes.OBJECT,
        404: CartErrorResponseSerializer,
    },
)


# =========================================================
# Clear
# =========================================================


cart_clear_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_clear",
    summary="Clear Cart",
    description=(
        "Removes all products and the applied "
        "discount code from the cart."
    ),
    request=None,
    responses={
        200: CartResponseSerializer,
        401: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Apply Discount
# =========================================================


cart_apply_discount_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_discount_apply",
    summary="Apply Discount Code",
    description=(
        "Validates and attaches a discount code "
        "to the cart. This does not consume the "
        "discount usage limit. Consumption occurs "
        "when an order is created."
    ),
    request=CartDiscountApplySerializer,
    examples=[
        OpenApiExample(
            name="Apply Discount",
            value=(
                examples
                .CART_APPLY_DISCOUNT_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=CartResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Discount Applied",
                    value=(
                        responses
                        .CartDiscountSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=CartErrorResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Invalid Discount",
                    value=(
                        responses
                        .CartInvalidDiscount
                    ),
                    response_only=True,
                )
            ],
        ),
        401: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Remove Discount
# =========================================================


cart_remove_discount_view_schema = extend_schema(
    tags=[
        "Cart",
    ],
    operation_id="cart_discount_remove",
    summary="Remove Discount Code",
    request=None,
    responses={
        200: CartResponseSerializer,
        401: OpenApiTypes.OBJECT,
    },
)