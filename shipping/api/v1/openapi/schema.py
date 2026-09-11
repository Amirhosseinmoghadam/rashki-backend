from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from shipping.api.v1.serializers import (
    ShippingMethodSerializer,
    ShippingQuoteRequestSerializer,
    ShippingQuoteSerializer,
    ShippingRateRuleSerializer,
)

from . import examples
from . import responses


# =========================================================
# Method Responses
# =========================================================


ShippingMethodListResponse = inline_serializer(
    name="ShippingMethodListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "count": serializers.IntegerField(),
        "data": ShippingMethodSerializer(
            many=True
        ),
    },
)


ShippingMethodDetailResponse = inline_serializer(
    name="ShippingMethodDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ShippingMethodSerializer(),
    },
)


# =========================================================
# Rate Responses
# =========================================================


ShippingRateListResponse = inline_serializer(
    name="ShippingRateListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "count": serializers.IntegerField(),
        "data": ShippingRateRuleSerializer(
            many=True
        ),
    },
)


ShippingRateDetailResponse = inline_serializer(
    name="ShippingRateDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ShippingRateRuleSerializer(),
    },
)


# =========================================================
# Generic Delete
# =========================================================


ShippingDeleteResponse = inline_serializer(
    name="ShippingDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True
        ),
    },
)


# =========================================================
# Quote Response
# =========================================================


ShippingQuoteDataSerializer = inline_serializer(
    name="ShippingQuoteData",
    fields={
        "address_id": serializers.IntegerField(),
        "province": serializers.CharField(),
        "city": serializers.CharField(),
        "weight_grams": serializers.IntegerField(),
        "quotes": ShippingQuoteSerializer(
            many=True
        ),
    },
)


ShippingQuoteResponse = inline_serializer(
    name="ShippingQuoteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ShippingQuoteDataSerializer,
    },
)


ShippingErrorResponse = inline_serializer(
    name="ShippingErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True
        ),
    },
)


# =========================================================
# Shipping Method
# =========================================================


shipping_method_list_schema = extend_schema(
    tags=["Shipping Methods"],
    auth=[],
    operation_id="shipping_method_list",
    summary="List Shipping Methods",
    responses={
        200: ShippingMethodListResponse,
    },
)


shipping_method_detail_schema = extend_schema(
    tags=["Shipping Methods"],
    auth=[],
    operation_id="shipping_method_detail",
    summary="Get Shipping Method",
    responses={
        200: ShippingMethodDetailResponse,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_method_create_schema = extend_schema(
    tags=["Shipping Methods Admin"],
    operation_id="shipping_method_create",
    summary="Create Shipping Method",
    request=ShippingMethodSerializer,
    examples=[
        OpenApiExample(
            name="Post Pishtaz",
            value=(
                examples
                .SHIPPING_METHOD_CREATE_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        201: ShippingMethodDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)


shipping_method_update_schema = extend_schema(
    tags=["Shipping Methods Admin"],
    operation_id="shipping_method_update",
    summary="Update Shipping Method",
    request=ShippingMethodSerializer,
    responses={
        200: ShippingMethodDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_method_partial_update_schema = extend_schema(
    tags=["Shipping Methods Admin"],
    operation_id="shipping_method_partial_update",
    summary="Partially Update Shipping Method",
    request=ShippingMethodSerializer,
    responses={
        200: ShippingMethodDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_method_delete_schema = extend_schema(
    tags=["Shipping Methods Admin"],
    operation_id="shipping_method_delete",
    summary="Delete Shipping Method",
    request=None,
    responses={
        200: ShippingDeleteResponse,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Rate Rule
# =========================================================


shipping_rate_list_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_list",
    summary="List Shipping Rate Rules",
    responses={
        200: ShippingRateListResponse,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)


shipping_rate_detail_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_detail",
    summary="Get Shipping Rate Rule",
    responses={
        200: ShippingRateDetailResponse,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_rate_create_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_create",
    summary="Create Shipping Rate Rule",
    request=ShippingRateRuleSerializer,
    examples=[
        OpenApiExample(
            name="Nationwide Rate",
            value=(
                examples
                .SHIPPING_RATE_CREATE_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        201: ShippingRateDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
    },
)


shipping_rate_update_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_update",
    request=ShippingRateRuleSerializer,
    responses={
        200: ShippingRateDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_rate_partial_update_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_partial_update",
    request=ShippingRateRuleSerializer,
    responses={
        200: ShippingRateDetailResponse,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


shipping_rate_delete_schema = extend_schema(
    tags=["Shipping Rates Admin"],
    operation_id="shipping_rate_delete",
    request=None,
    responses={
        200: ShippingDeleteResponse,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Quote
# =========================================================


shipping_quote_schema = extend_schema(
    tags=["Shipping"],
    operation_id="shipping_quote",
    summary="Calculate Shipping Quotes",
    description=(
        "Calculates currently available shipping options "
        "for the authenticated user's cart and selected "
        "saved address. All monetary values are Toman."
    ),
    request=ShippingQuoteRequestSerializer,
    examples=[
        OpenApiExample(
            name="Shipping Quote",
            value=(
                examples
                .SHIPPING_QUOTE_EXAMPLE
            ),
            request_only=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ShippingQuoteResponse,
            examples=[
                OpenApiExample(
                    name="Quote Success",
                    value=(
                        responses
                        .ShippingQuoteSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=ShippingErrorResponse,
            examples=[
                OpenApiExample(
                    name="Invalid Address",
                    value=(
                        responses
                        .ShippingInvalidAddress
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Missing Product Weight",
                    value=(
                        responses
                        .ShippingMissingWeight
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiTypes.OBJECT,
    },
)