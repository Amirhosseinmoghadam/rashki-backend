from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from discounts.api.v1.serializers import (
    DiscountCodeSerializer,
    DiscountValidateSerializer,
    DiscountCalculationSerializer,
)

from . import examples
from . import responses


# =========================================================
# Generic Responses
# =========================================================


DiscountListResponseSerializer = inline_serializer(
    name="DiscountListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "count": serializers.IntegerField(),
        "data": DiscountCodeSerializer(
            many=True
        ),
    },
)


DiscountDetailResponseSerializer = inline_serializer(
    name="DiscountDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": DiscountCodeSerializer(),
    },
)


DiscountDeleteResponseSerializer = inline_serializer(
    name="DiscountDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True
        ),
    },
)


DiscountErrorResponseSerializer = inline_serializer(
    name="DiscountErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True
        ),
    },
)


DiscountValidationResponseSerializer = inline_serializer(
    name="DiscountValidationResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": DiscountCalculationSerializer(),
    },
)


# =========================================================
# Admin List
# =========================================================


discount_list_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_list",
    summary="List Discount Codes",
    responses={
        200: DiscountListResponseSerializer,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Admin Detail
# =========================================================


discount_detail_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_detail",
    summary="Get Discount Code",
    responses={
        200: DiscountDetailResponseSerializer,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Admin Create
# =========================================================


discount_create_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_create",
    summary="Create Discount Code",
    request=DiscountCodeSerializer,
    examples=[
        OpenApiExample(
            name="Percentage Discount",
            value=(
                examples
                .DISCOUNT_PERCENTAGE_CREATE_EXAMPLE
            ),
            request_only=True,
        ),
        OpenApiExample(
            name="Fixed Discount",
            value=(
                examples
                .DISCOUNT_FIXED_CREATE_EXAMPLE
            ),
            request_only=True,
        ),
        OpenApiExample(
            name="Product Specific Discount",
            value=(
                examples
                .DISCOUNT_PRODUCT_SCOPE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        201: DiscountDetailResponseSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Admin Update
# =========================================================


discount_update_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_update",
    summary="Update Discount Code",
    request=DiscountCodeSerializer,
    responses={
        200: DiscountDetailResponseSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Admin PATCH
# =========================================================


discount_partial_update_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_partial_update",
    summary="Partially Update Discount Code",
    request=DiscountCodeSerializer,
    responses={
        200: DiscountDetailResponseSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Admin Delete
# =========================================================


discount_delete_view_schema = extend_schema(
    tags=[
        "Discounts Admin",
    ],
    operation_id="discount_delete",
    summary="Delete Discount Code",
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                DiscountDeleteResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Deleted",
                    value=(
                        responses
                        .DiscountDeleteSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        409: OpenApiResponse(
            response=(
                DiscountErrorResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Protected",
                    value=(
                        responses
                        .DiscountDeleteProtected
                    ),
                    response_only=True,
                )
            ],
        ),
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# User Validate
# =========================================================


discount_validate_view_schema = extend_schema(
    tags=[
        "Discounts",
    ],
    operation_id="discount_validate",
    summary="Validate Discount Code",
    description=(
        "Validates a discount code against the submitted "
        "products. Product prices are loaded from the "
        "backend and are not accepted from the client. "
        "Shipping is not included in discount calculation."
    ),
    request=DiscountValidateSerializer,
    examples=[
        OpenApiExample(
            name="Validate Discount",
            value=(
                examples
                .DISCOUNT_VALIDATE_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=(
                DiscountValidationResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Valid Discount",
                    value=(
                        responses
                        .DiscountValidateSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=(
                DiscountErrorResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Invalid Code",
                    value=(
                        responses
                        .DiscountInvalidCode
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Expired",
                    value=(
                        responses
                        .DiscountExpired
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Minimum Order",
                    value=(
                        responses
                        .DiscountMinimumOrder
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Usage Limit",
                    value=(
                        responses
                        .DiscountUsageLimitReached
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="User Limit",
                    value=(
                        responses
                        .DiscountUserLimitReached
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="No Eligible Product",
                    value=(
                        responses
                        .DiscountNoEligibleProduct
                    ),
                    response_only=True,
                ),
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