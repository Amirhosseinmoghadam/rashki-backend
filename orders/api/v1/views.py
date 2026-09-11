from drf_spectacular.utils import (
    extend_schema_view,
)

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import (
    Response,
)

from orders.cancellation import (
    OrderCancellationError,
    OrderCancellationReviewRequired,
    cancel_order_with_refund,
)

from orders.models import (
    Order,
)

from orders.selectors import (
    get_user_orders,
)

from orders.services import (
    OrderValidationError,
    create_order_from_cart,
)

from utils.pagination import (
    DefaultPagination,
)

from .openapi.schema import (
    order_cancel_schema,
    order_detail_schema,
    order_list_create_schema,
)

from .serializers import (
    OrderCancellationRequestSerializer,
    OrderCancellationResultSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


# =========================================================
# List / Create
# =========================================================


class OrderListCreateAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    pagination_class = (
        DefaultPagination
    )

    # =====================================================
    # GET
    # =====================================================

    @order_list_create_schema["get"]
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = (
            get_user_orders(
                request.user
            )
        )

        page = (
            self.paginate_queryset(
                queryset
            )
        )

        serializer = (
            OrderListSerializer(
                page,
                many=True,
            )
        )

        pagination_data = (
            self
            .get_paginated_response(
                serializer.data
            )
            .data
        )

        return Response(
            {
                "success": True,

                "message": (
                    "لیست سفارش‌ها با موفقیت "
                    "دریافت شد."
                ),

                "data": (
                    pagination_data
                ),
            },

            status=(
                status.HTTP_200_OK
            ),
        )

    # =====================================================
    # POST
    # =====================================================

    @order_list_create_schema["post"]
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = (
            OrderCreateSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            order = (
                create_order_from_cart(

                    user=(
                        request.user
                    ),

                    address_id=(
                        serializer
                        .validated_data[
                            "address_id"
                        ]
                    ),

                    shipping_method_id=(
                        serializer
                        .validated_data[
                            "shipping_method_id"
                        ]
                    ),

                    accept_terms=(
                        serializer
                        .validated_data[
                            "accept_terms"
                        ]
                    ),

                    customer_note=(
                        serializer
                        .validated_data
                        .get(
                            "customer_note",
                            "",
                        )
                    ),
                )
            )

        except OrderValidationError as exc:

            return Response(
                {
                    "success": False,

                    "message": (
                        str(exc)
                    ),

                    "errors": None,
                },

                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "success": True,

                "message": (
                    "سفارش با موفقیت "
                    "ثبت شد."
                ),

                "data": (
                    OrderDetailSerializer(
                        order
                    ).data
                ),
            },

            status=(
                status.HTTP_201_CREATED
            ),
        )


# =========================================================
# Detail
# =========================================================


class OrderDetailAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    @order_detail_schema
    def get(
        self,
        request,
        order_number,
        *args,
        **kwargs,
    ):

        order = (
            get_user_orders(
                request.user
            )
            .filter(
                order_number=(
                    order_number
                )
            )
            .first()
        )

        if order is None:

            return Response(
                {
                    "success": False,

                    "message": (
                        "سفارش موردنظر یافت نشد."
                    ),

                    "errors": None,
                },

                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            {
                "success": True,

                "message": (
                    "سفارش با موفقیت "
                    "دریافت شد."
                ),

                "data": (
                    OrderDetailSerializer(
                        order
                    ).data
                ),
            },

            status=(
                status.HTTP_200_OK
            ),
        )


# =========================================================
# Cancel Order
# =========================================================


@extend_schema_view(
    post=order_cancel_schema,
)
class OrderCancelAPIView(
    generics.GenericAPIView
):
    """
    لغو امن Order.

    Customer:
        فقط سفارش خودش.

    Admin:
        هر سفارش.

    برای سفارش پرداخت‌شده:

        Shipment cancellation
            ↓
        Refund / Reversal
            ↓
        Cancel Order
            ↓
        Restore Stock
    """

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        OrderCancellationRequestSerializer
    )

    # =====================================================
    # POST
    # =====================================================

    def post(
        self,
        request,
        order_number,
        *args,
        **kwargs,
    ):

        # =================================================
        # Request Validation
        # =================================================

        serializer = (
            self.get_serializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        # =================================================
        # Order Access
        # =================================================

        queryset = (
            Order.objects.all()
        )

        # Customer فقط سفارش خودش را می‌بیند.
        # Staff می‌تواند هر سفارش را مدیریت کند.
        if not request.user.is_staff:

            queryset = (
                queryset.filter(
                    user=request.user
                )
            )

        order = (
            queryset
            .filter(
                order_number=(
                    order_number
                )
            )
            .first()
        )

        # =================================================
        # Not Found
        # =================================================

        if order is None:

            return Response(
                {
                    "success": False,

                    "message": (
                        "سفارش موردنظر یافت نشد."
                    ),

                    "errors": None,
                },

                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        # =================================================
        # Cancellation Workflow
        # =================================================

        try:

            result = (
                cancel_order_with_refund(

                    order=order,

                    reason=(
                        serializer
                        .validated_data
                        .get(
                            "reason",
                            "customer_request",
                        )
                    ),

                    description=(
                        serializer
                        .validated_data
                        .get(
                            "description",
                            "",
                        )
                    ),

                    # -------------------------------------
                    # Backend-controlled Idempotency
                    # -------------------------------------
                    #
                    # Client اجازه تعیین Idempotency-Key
                    # مربوط به Refund مالی را ندارد.
                    # -------------------------------------

                    refund_idempotency_key=(
                        f"order-cancellation-"
                        f"{order.id}-"
                        f"full-refund-v1"
                    ),
                )
            )

        # =================================================
        # Manual Review Required
        # =================================================
        #
        # مثال:
        #
        # - Tipax Cancel Timeout
        # - ZarinPal Reversal Timeout
        #
        # در این حالت Retry خودکار نباید انجام شود.
        # =================================================

        except (
            OrderCancellationReviewRequired
        ) as exc:

            return Response(
                {
                    "success": False,

                    "message": (
                        str(exc)
                    ),

                    "errors": {
                        "review_required": True,
                    },
                },

                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        # =================================================
        # Definite Cancellation Failure
        # =================================================

        except OrderCancellationError as exc:

            return Response(
                {
                    "success": False,

                    "message": (
                        str(exc)
                    ),

                    "errors": None,
                },

                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                ),
            )

        # =================================================
        # Result Objects
        # =================================================

        shipment = (
            result.shipment
        )

        refund = (
            result.refund
        )

        # =================================================
        # Response Data
        # =================================================

        response_data = {

            "order_number": (
                result
                .order
                .order_number
            ),

            "order_status": (
                result
                .order
                .status
            ),

            "payment_status": (
                result
                .order
                .payment_status
            ),

            "already_cancelled": (
                result
                .already_cancelled
            ),

            # ---------------------------------------------
            # Shipment
            # ---------------------------------------------

            "shipment_id": (
                shipment.id
                if shipment
                else None
            ),

            "shipment_status": (
                shipment.status
                if shipment
                else None
            ),

            # ---------------------------------------------
            # Refund
            # ---------------------------------------------

            "refund_public_id": (
                refund.public_id
                if refund
                else None
            ),

            "refund_status": (
                refund.status
                if refund
                else None
            ),
        }

        # =================================================
        # Response Serializer
        # =================================================

        response_serializer = (
            OrderCancellationResultSerializer(
                response_data
            )
        )

        # =================================================
        # Success Response
        # =================================================

        return Response(
            {
                "success": True,

                "message": (
                    "سفارش قبلاً لغو شده است."
                    if result.already_cancelled
                    else
                    "سفارش با موفقیت لغو شد."
                ),

                "data": (
                    response_serializer.data
                ),
            },

            status=(
                status.HTTP_200_OK
            ),
        )