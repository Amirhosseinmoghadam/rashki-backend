
from orders.api.v1.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderCancellationRequestSerializer,
    OrderCancellationResultSerializer,
)

from . import examples
from . import responses
from rest_framework import serializers

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

# =========================================================
# Responses
# =========================================================


OrderDetailResponse = inline_serializer(
    name="OrderDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": OrderDetailSerializer(),
    },
)


OrderPaginationData = inline_serializer(
    name="OrderPaginationData",
    fields={
        "count": serializers.IntegerField(),

        "next": serializers.URLField(
            allow_null=True
        ),

        "previous": serializers.URLField(
            allow_null=True
        ),

        "results": OrderListSerializer(
            many=True
        ),
    },
)


OrderListResponse = inline_serializer(
    name="OrderListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": OrderPaginationData,
    },
)


OrderErrorResponse = inline_serializer(
    name="OrderErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True
        ),
    },
)


# =========================================================
# GET Orders
# =========================================================


order_list_schema = extend_schema(
    tags=["Orders"],
    operation_id="order_list",
    summary="List User Orders",
    responses={
        200: OrderListResponse,
        401: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# POST Order
# =========================================================


order_create_schema = extend_schema(
    tags=["Orders"],
    operation_id="order_create",
    summary="Create Order From Cart",
    description=(
        "Creates an immutable order snapshot from the "
        "authenticated user's cart. Product prices, "
        "stock, discount and shipping price are "
        "revalidated on the backend."
    ),
    request=OrderCreateSerializer,
    examples=[
        OpenApiExample(
            name="Checkout",
            value=(
                examples
                .ORDER_CREATE_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        201: OpenApiResponse(
            response=OrderDetailResponse,
            examples=[
                OpenApiExample(
                    name="Order Created",
                    value=(
                        responses
                        .OrderCreateSuccess
                    ),
                    response_only=True,
                )
            ],
        ),

        400: OpenApiResponse(
            response=OrderErrorResponse,
            examples=[
                OpenApiExample(
                    name="Stock Error",
                    value=(
                        responses
                        .OrderInvalidStock
                    ),
                    response_only=True,
                ),

                OpenApiExample(
                    name="Address Error",
                    value=(
                        responses
                        .OrderInvalidAddress
                    ),
                    response_only=True,
                ),

                OpenApiExample(
                    name="Shipping Error",
                    value=(
                        responses
                        .OrderInvalidShipping
                    ),
                    response_only=True,
                ),
            ],
        ),

        401: OpenApiTypes.OBJECT,
    },
)


# در views.py برای اینکه GET و POST
# decorator جدا داشته باشند:
order_list_create_schema = {
    "get": order_list_schema,
    "post": order_create_schema,
}


# =========================================================
# Detail
# =========================================================


order_detail_schema = extend_schema(
    tags=["Orders"],
    operation_id="order_detail",
    summary="Get Order Detail",
    parameters=[
        OpenApiParameter(
            name="order_number",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.PATH
            ),
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=OrderDetailResponse,
            examples=[
                OpenApiExample(
                    name="Order",
                    value={
                        "success": True,
                        "message": (
                            "سفارش با موفقیت "
                            "دریافت شد."
                        ),
                        "data": (
                            responses
                            .OrderExample
                        ),
                    },
                    response_only=True,
                )
            ],
        ),

        401: OpenApiTypes.OBJECT,

        404: OpenApiResponse(
            response=OrderErrorResponse,
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=(
                        responses
                        .OrderNotFound
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Cancel
# =========================================================


order_cancel_schema = extend_schema(
    tags=["Orders"],
    operation_id="order_cancel",
    summary="Cancel Unpaid Order",
    description=(
        "Cancels an unpaid order, restores reserved "
        "stock and revokes the consumed discount usage."
    ),
    request=None,
    parameters=[
        OpenApiParameter(
            name="order_number",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.PATH
            ),
            required=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=OrderDetailResponse,
            examples=[
                OpenApiExample(
                    name="Cancelled",
                    value=(
                        responses
                        .OrderCancelSuccess
                    ),
                    response_only=True,
                )
            ],
        ),

        401: OpenApiTypes.OBJECT,

        404: OrderErrorResponse,

        409: OrderErrorResponse,
    },
)

# =========================================================
# Order Cancellation Response Serializers
# =========================================================


OrderCancellationSuccessResponseSerializer = (
    inline_serializer(
        name="OrderCancellationSuccessResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),

            "message": (
                serializers.CharField()
            ),

            "data": (
                OrderCancellationResultSerializer()
            ),
        },
    )
)


OrderCancellationErrorResponseSerializer = (
    inline_serializer(
        name="OrderCancellationErrorResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),

            "message": (
                serializers.CharField()
            ),

            "errors": (
                serializers.JSONField(
                    allow_null=True,
                )
            ),
        },
    )
)


# =========================================================
# Order Cancellation Schema
# =========================================================


order_cancel_schema = extend_schema(

    tags=[
        "Orders",
    ],

    operation_id=(
        "order_cancel"
    ),

    summary=(
        "Cancel Order"
    ),

    description=(
        "Cancels an order belonging to the authenticated "
        "user. Staff users may cancel any order.\n\n"

        "For an unpaid order, the reserved stock is "
        "released immediately and no refund is created.\n\n"

        "For a paid order, the cancellation workflow may "
        "first cancel the external shipment and then "
        "execute the payment refund/reversal.\n\n"

        "If the result of an external operation such as "
        "Tipax cancellation or ZarinPal reversal is "
        "indeterminate, the endpoint returns HTTP 409 "
        "with review_required=true. In this situation "
        "automatic retries must not be performed."
    ),

    parameters=[
        OpenApiParameter(
            name="order_number",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.PATH
            ),
            required=True,
            description=(
                "Public order number."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Order Number"
                    ),
                    value=(
                        "RK-20260911-15E6223F"
                    ),
                ),
            ],
        ),
    ],

    request=(
        OrderCancellationRequestSerializer
    ),

    examples=[
        OpenApiExample(
            name=(
                "Cancel Order Request"
            ),
            value=(
                examples
                .OrderCancellationRequestExample
            ),
            request_only=True,
        ),
    ],

    responses={

        # =================================================
        # 200
        # =================================================

        200: OpenApiResponse(
            response=(
                OrderCancellationSuccessResponseSerializer
            ),
            description=(
                "Order cancelled successfully or "
                "the order was already cancelled."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Cancellation Successful"
                    ),
                    value=(
                        responses
                        .OrderCancellationSuccess
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),

                OpenApiExample(
                    name=(
                        "Already Cancelled"
                    ),
                    value=(
                        responses
                        .OrderCancellationAlreadyCancelled
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),
            ],
        ),

        # =================================================
        # 400
        # =================================================

        400: OpenApiResponse(
            response=(
                OrderCancellationErrorResponseSerializer
            ),
            description=(
                "The order cannot be cancelled "
                "because of its current state."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Cancellation Not Allowed"
                    ),
                    value=(
                        responses
                        .OrderCancellationValidationError
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),
            ],
        ),

        # =================================================
        # 401
        # =================================================

        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Authentication required."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Authentication Required"
                    ),
                    value=(
                        responses
                        .OrderCancellationAuthenticationRequired
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),
            ],
        ),

        # =================================================
        # 404
        # =================================================

        404: OpenApiResponse(
            response=(
                OrderCancellationErrorResponseSerializer
            ),
            description=(
                "Order not found or the authenticated "
                "user does not have access to it."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Order Not Found"
                    ),
                    value=(
                        responses
                        .OrderCancellationNotFound
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),
            ],
        ),

        # =================================================
        # 409
        # =================================================

        409: OpenApiResponse(
            response=(
                OrderCancellationErrorResponseSerializer
            ),
            description=(
                "The cancellation workflow requires "
                "manual review or reconciliation. "
                "Automatic retry must not be performed."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Manual Review Required"
                    ),
                    value=(
                        responses
                        .OrderCancellationReviewRequired
                    ),
                    media_type=(
                        "application/json"
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)