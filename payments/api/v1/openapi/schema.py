from rest_framework import serializers

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from payments.api.v1.serializers import (
    PaymentAttemptSerializer,
    PaymentRefundCreateSerializer,
    PaymentRefundSerializer,
    PaymentStartSerializer,
)

from . import examples
from . import responses


# =========================================================
# Response Schemas
# =========================================================


PaymentAttemptResponse = inline_serializer(
    name="PaymentAttemptResponse",

    fields={
        "success": (
            serializers.BooleanField()
        ),

        "message": (
            serializers.CharField()
        ),

        "data": (
            PaymentAttemptSerializer()
        ),
    },
)


PaymentErrorResponse = inline_serializer(
    name="PaymentErrorResponse",

    fields={
        "success": (
            serializers.BooleanField()
        ),

        "message": (
            serializers.CharField()
        ),

        "errors": (
            serializers.JSONField(
                allow_null=True
            )
        ),
    },
)


# =========================================================
# Refund Response Schemas
# =========================================================


PaymentRefundResponse = inline_serializer(
    name="PaymentRefundResponse",

    fields={
        "success": (
            serializers.BooleanField()
        ),

        "message": (
            serializers.CharField()
        ),

        "data": (
            PaymentRefundSerializer()
        ),
    },
)


PaymentRefundErrorResponse = inline_serializer(
    name="PaymentRefundErrorResponse",

    fields={
        "success": (
            serializers.BooleanField()
        ),

        "message": (
            serializers.CharField()
        ),

        "errors": (
            serializers.JSONField(
                allow_null=True
            )
        ),
    },
)


PaymentRefundExecutionErrorResponse = (
    inline_serializer(
        name=(
            "PaymentRefundExecutionErrorResponse"
        ),

        fields={
            "success": (
                serializers.BooleanField()
            ),

            "message": (
                serializers.CharField()
            ),

            "data": (
                PaymentRefundSerializer()
            ),

            "errors": (
                serializers.JSONField(
                    allow_null=True
                )
            ),
        },
    )
)


# =========================================================
# Start Payment
# =========================================================


payment_start_schema = extend_schema(

    tags=[
        "Payments",
    ],

    operation_id="payment_start",

    summary="Start Payment",

    description=(
        "Creates or reuses a payment attempt for an "
        "unpaid order. Provider amounts are calculated "
        "by the backend. The client must never submit "
        "payment amounts."
    ),

    request=PaymentStartSerializer,

    examples=[

        OpenApiExample(
            name="ZarinPal",

            value=(
                examples
                .PAYMENT_START_ZARINPAL_EXAMPLE
            ),

            request_only=True,
        ),

        OpenApiExample(
            name="TCart",

            value=(
                examples
                .PAYMENT_START_TCART_EXAMPLE
            ),

            request_only=True,
        ),
    ],

    responses={

        200: OpenApiResponse(
            response=(
                PaymentAttemptResponse
            ),

            examples=[
                OpenApiExample(
                    name="Payment Started",

                    value=(
                        responses
                        .PaymentStartSuccess
                    ),

                    response_only=True,
                )
            ],
        ),

        400: OpenApiResponse(
            response=(
                PaymentErrorResponse
            ),

            examples=[

                OpenApiExample(
                    name="Already Paid",

                    value=(
                        responses
                        .PaymentAlreadyPaid
                    ),

                    response_only=True,
                ),

                OpenApiExample(
                    name="Expired",

                    value=(
                        responses
                        .PaymentExpiredOrder
                    ),

                    response_only=True,
                ),

                OpenApiExample(
                    name="Provider Error",

                    value=(
                        responses
                        .PaymentProviderError
                    ),

                    response_only=True,
                ),
            ],
        ),

        401: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Payment Detail
# =========================================================


payment_detail_schema = extend_schema(

    tags=[
        "Payments",
    ],

    operation_id="payment_detail",

    summary="Get Payment Attempt",

    parameters=[

        OpenApiParameter(
            name="public_id",

            type=OpenApiTypes.UUID,

            location=(
                OpenApiParameter.PATH
            ),

            required=True,
        )
    ],

    responses={

        200: PaymentAttemptResponse,

        401: OpenApiTypes.OBJECT,

        404: OpenApiResponse(
            response=(
                PaymentErrorResponse
            ),

            examples=[
                OpenApiExample(
                    name="Not Found",

                    value=(
                        responses
                        .PaymentNotFound
                    ),

                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# ZarinPal Callback
# =========================================================


zarinpal_callback_schema = extend_schema(

    tags=[
        "Payments - Callbacks",
    ],

    auth=[],

    operation_id=(
        "zarinpal_callback"
    ),

    summary="ZarinPal Callback",

    description=(
        "Public callback used by ZarinPal. "
        "The callback itself is not trusted; "
        "the backend verifies the payment directly "
        "with ZarinPal before marking the order paid."
    ),

    parameters=[

        OpenApiParameter(
            name="public_id",

            type=OpenApiTypes.UUID,

            location=(
                OpenApiParameter.PATH
            ),

            required=True,
        ),

        OpenApiParameter(
            name="Authority",

            type=OpenApiTypes.STR,

            location=(
                OpenApiParameter.QUERY
            ),

            required=True,
        ),

        OpenApiParameter(
            name="Status",

            type=OpenApiTypes.STR,

            location=(
                OpenApiParameter.QUERY
            ),

            required=True,
        ),
    ],

    responses={

        302: OpenApiResponse(
            description=(
                "Redirects the user's browser to "
                "the frontend payment result page."
            )
        )
    },
)


# =========================================================
# TCart Callback
# =========================================================


tcart_callback_schema = extend_schema(

    tags=[
        "Payments - Callbacks",
    ],

    auth=[],

    operation_id=(
        "tcart_callback"
    ),

    summary="TCart Webhook",

    description=(
        "Reserved callback endpoint for TCart. "
        "The exact HMAC verification contract will be "
        "implemented from TCart's API documentation "
        "before production use."
    ),

    parameters=[

        OpenApiParameter(
            name="public_id",

            type=OpenApiTypes.UUID,

            location=(
                OpenApiParameter.PATH
            ),

            required=True,
        ),
    ],

    request=OpenApiTypes.OBJECT,

    responses={

        200: OpenApiTypes.OBJECT,

        404: OpenApiTypes.OBJECT,

        503: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Create Refund
# =========================================================


payment_refund_create_schema = extend_schema(

    tags=[
        "Payments - Refunds",
    ],

    operation_id=(
        "payment_refund_create"
    ),

    summary="Create Payment Refund",

    description=(
        "Creates a refund record for a successful "
        "payment. This endpoint does not immediately "
        "send the financial request to the provider. "
        "Only admin users can use this endpoint. "
        "Use the Idempotency-Key header to safely "
        "repeat the same request."
    ),

    request=(
        PaymentRefundCreateSerializer
    ),

    parameters=[

        OpenApiParameter(
            name="Idempotency-Key",

            type=OpenApiTypes.STR,

            location=(
                OpenApiParameter.HEADER
            ),

            required=False,

            description=(
                "Optional idempotency key. "
                "Repeating the same request with the "
                "same key returns the existing refund."
            ),
        ),
    ],

    examples=[

        OpenApiExample(
            name="Full Refund",

            value=(
                examples
                .PAYMENT_REFUND_FULL_EXAMPLE
            ),

            request_only=True,
        ),

        OpenApiExample(
            name="Partial Refund",

            value=(
                examples
                .PAYMENT_REFUND_PARTIAL_EXAMPLE
            ),

            request_only=True,
        ),
    ],

    responses={

        201: OpenApiResponse(
            response=(
                PaymentRefundResponse
            ),

            description=(
                "Refund record created successfully."
            ),

            examples=[
                OpenApiExample(
                    name="Refund Created",

                    value=(
                        responses
                        .PaymentRefundCreated
                    ),

                    response_only=True,
                )
            ],
        ),

        200: OpenApiResponse(
            response=(
                PaymentRefundResponse
            ),

            description=(
                "An existing refund was returned "
                "because the Idempotency-Key was "
                "already used."
            ),

            examples=[
                OpenApiExample(
                    name="Existing Refund",

                    value=(
                        responses
                        .PaymentRefundAlreadyExists
                    ),

                    response_only=True,
                )
            ],
        ),

        400: OpenApiResponse(
            response=(
                PaymentRefundErrorResponse
            ),

            description=(
                "Refund validation failed."
            ),

            examples=[

                OpenApiExample(
                    name="No Successful Payment",

                    value=(
                        responses
                        .PaymentRefundNoSuccessfulPayment
                    ),

                    response_only=True,
                ),

                OpenApiExample(
                    name="Over Refund",

                    value=(
                        responses
                        .PaymentRefundOverAmount
                    ),

                    response_only=True,
                ),

                OpenApiExample(
                    name="Fully Reserved",

                    value=(
                        responses
                        .PaymentRefundAlreadyFullyReserved
                    ),

                    response_only=True,
                ),
            ],
        ),

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
                        .PaymentAuthenticationRequired
                    ),

                    response_only=True,
                )
            ],
        ),

        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,

            description=(
                "Admin permission required."
            ),

            examples=[
                OpenApiExample(
                    name="Permission Denied",

                    value=(
                        responses
                        .PaymentRefundPermissionDenied
                    ),

                    response_only=True,
                )
            ],
        ),

        404: OpenApiResponse(
            response=(
                PaymentRefundErrorResponse
            ),

            description=(
                "Order not found."
            ),

            examples=[
                OpenApiExample(
                    name="Order Not Found",

                    value=(
                        responses
                        .PaymentRefundOrderNotFound
                    ),

                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Refund Detail
# =========================================================


payment_refund_detail_schema = extend_schema(

    tags=[
        "Payments - Refunds",
    ],

    operation_id=(
        "payment_refund_detail"
    ),

    summary="Get Payment Refund",

    description=(
        "Returns the current state and audit "
        "information for a refund. "
        "Only admin users can use this endpoint."
    ),

    parameters=[

        OpenApiParameter(
            name="public_id",

            type=OpenApiTypes.UUID,

            location=(
                OpenApiParameter.PATH
            ),

            required=True,
        ),
    ],

    responses={

        200: OpenApiResponse(
            response=(
                PaymentRefundResponse
            ),

            examples=[
                OpenApiExample(
                    name="Refund Detail",

                    value=(
                        responses
                        .PaymentRefundDetail
                    ),

                    response_only=True,
                )
            ],
        ),

        401: OpenApiTypes.OBJECT,

        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,

            examples=[
                OpenApiExample(
                    name="Permission Denied",

                    value=(
                        responses
                        .PaymentRefundPermissionDenied
                    ),

                    response_only=True,
                )
            ],
        ),

        404: OpenApiResponse(
            response=(
                PaymentRefundErrorResponse
            ),

            examples=[
                OpenApiExample(
                    name="Refund Not Found",

                    value=(
                        responses
                        .PaymentRefundNotFound
                    ),

                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Execute Refund
# =========================================================


payment_refund_execute_schema = extend_schema(

    tags=[
        "Payments - Refunds",
    ],

    operation_id=(
        "payment_refund_execute"
    ),

    summary="Execute Payment Refund",

    description=(
        "Executes the external financial refund "
        "operation for an existing refund record. "
        "Only admin users can use this endpoint. "
        "A provider/network result that cannot be "
        "determined safely is moved to "
        "requires_review and must not be retried "
        "automatically."
    ),

    parameters=[

        OpenApiParameter(
            name="public_id",

            type=OpenApiTypes.UUID,

            location=(
                OpenApiParameter.PATH
            ),

            required=True,
        ),
    ],

    request=None,

    responses={

        200: OpenApiResponse(
            response=(
                PaymentRefundResponse
            ),

            description=(
                "Refund completed successfully "
                "or had already completed."
            ),

            examples=[
                OpenApiExample(
                    name="Refund Executed",

                    value=(
                        responses
                        .PaymentRefundExecuted
                    ),

                    response_only=True,
                )
            ],
        ),

        400: OpenApiResponse(
            response=(
                PaymentRefundExecutionErrorResponse
            ),

            description=(
                "Refund cannot be executed because "
                "of its current business state."
            ),
        ),

        401: OpenApiTypes.OBJECT,

        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,

            examples=[
                OpenApiExample(
                    name="Permission Denied",

                    value=(
                        responses
                        .PaymentRefundPermissionDenied
                    ),

                    response_only=True,
                )
            ],
        ),

        404: OpenApiResponse(
            response=(
                PaymentRefundErrorResponse
            ),

            examples=[
                OpenApiExample(
                    name="Refund Not Found",

                    value=(
                        responses
                        .PaymentRefundNotFound
                    ),

                    response_only=True,
                )
            ],
        ),

        409: OpenApiResponse(
            response=(
                PaymentRefundExecutionErrorResponse
            ),

            description=(
                "The provider result is unknown and "
                "the refund requires manual review."
            ),

            examples=[
                OpenApiExample(
                    name="Requires Review",

                    value=(
                        responses
                        .PaymentRefundRequiresReview
                    ),

                    response_only=True,
                )
            ],
        ),

        502: OpenApiResponse(
            response=(
                PaymentRefundExecutionErrorResponse
            ),

            description=(
                "The payment provider definitively "
                "rejected the refund."
            ),

            examples=[
                OpenApiExample(
                    name="Provider Rejected",

                    value=(
                        responses
                        .PaymentRefundProviderRejected
                    ),

                    response_only=True,
                )
            ],
        ),
    },
)