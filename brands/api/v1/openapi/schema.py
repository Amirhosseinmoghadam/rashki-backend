from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from brands.api.v1.serializers import (
    BrandListSerializer,
    BrandDetailSerializer,
    BrandCreateUpdateSerializer,
)

from . import examples
from . import responses


# =========================================================
# Reusable Response Serializers
# =========================================================


BrandListResponseSerializer = inline_serializer(
    name="BrandListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "count": serializers.IntegerField(),
        "data": BrandListSerializer(
            many=True,
        ),
    },
)


BrandDetailResponseSerializer = inline_serializer(
    name="BrandDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": BrandDetailSerializer(),
    },
)


BrandMutationResponseSerializer = inline_serializer(
    name="BrandMutationResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": BrandDetailSerializer(),
    },
)


BrandDeleteResponseSerializer = inline_serializer(
    name="BrandDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True,
        ),
    },
)


BrandDeleteProtectedResponseSerializer = (
    inline_serializer(
        name="BrandDeleteProtectedResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "errors": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


# =========================================================
# Brand List
# =========================================================


brand_list_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    auth=[],
    operation_id="brand_list",
    summary="List Brands",
    description=(
        "Returns all active product brands. "
        "This endpoint is publicly accessible. "
        "Brands can optionally be searched by "
        "name or description."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Search active brands by "
                "name or description."
            ),
            examples=[
                OpenApiExample(
                    name="Search Brand",
                    value="NGK",
                ),
            ],
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                BrandListResponseSerializer
            ),
            description=(
                "Brands retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brands Retrieved",
                    value=(
                        responses
                        .BrandListAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Brand Detail
# =========================================================


brand_detail_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    auth=[],
    operation_id="brand_detail",
    summary="Get Brand",
    description=(
        "Returns a single active product brand. "
        "This endpoint is publicly accessible."
    ),
    responses={
        200: OpenApiResponse(
            response=(
                BrandDetailResponseSerializer
            ),
            description=(
                "Brand retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brand Retrieved",
                    value=(
                        responses
                        .BrandDetailAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
            examples=[
                OpenApiExample(
                    name="Brand Not Found",
                    value=(
                        responses
                        .BrandNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Brand Create
# =========================================================


brand_create_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    operation_id="brand_create",
    summary="Create Brand",
    description=(
        "Creates a new product brand. "
        "Only admin users can use this endpoint. "
        "The slug is generated automatically "
        "and cannot be submitted manually."
    ),
    request=BrandCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Create Brand",
            value=(
                examples
                .BRAND_CREATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                BrandMutationResponseSerializer
            ),
            description=(
                "Brand created successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brand Created",
                    value=(
                        responses
                        .BrandCreateAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
            examples=[
                OpenApiExample(
                    name="Validation Error",
                    value=(
                        responses
                        .BrandValidationError
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Duplicate Brand",
                    value=(
                        responses
                        .BrandDuplicateName
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Image",
                    value=(
                        responses
                        .BrandInvalidImage
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Website",
                    value=(
                        responses
                        .BrandInvalidWebsite
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    name=(
                        "Authentication Required"
                    ),
                    value=(
                        responses
                        .BrandAuthenticationRequired
                    ),
                    response_only=True,
                ),
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
                        .BrandPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Brand Update
# =========================================================


brand_update_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    operation_id="brand_update",
    summary="Update Brand",
    description=(
        "Fully updates an existing brand. "
        "Only admin users can use this endpoint. "
        "The slug remains unchanged when the "
        "brand name changes."
    ),
    request=BrandCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Update Brand",
            value=(
                examples
                .BRAND_UPDATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                BrandMutationResponseSerializer
            ),
            description=(
                "Brand updated successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brand Updated",
                    value=(
                        responses
                        .BrandUpdateAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
            examples=[
                OpenApiExample(
                    name="Duplicate Brand",
                    value=(
                        responses
                        .BrandDuplicateName
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Image",
                    value=(
                        responses
                        .BrandInvalidImage
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Website",
                    value=(
                        responses
                        .BrandInvalidWebsite
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    name=(
                        "Authentication Required"
                    ),
                    value=(
                        responses
                        .BrandAuthenticationRequired
                    ),
                    response_only=True,
                ),
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
                        .BrandPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
            examples=[
                OpenApiExample(
                    name="Brand Not Found",
                    value=(
                        responses
                        .BrandNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Brand Partial Update
# =========================================================


brand_partial_update_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    operation_id="brand_partial_update",
    summary="Partially Update Brand",
    description=(
        "Partially updates an existing brand. "
        "Only submitted fields are modified. "
        "The slug cannot be changed."
    ),
    request=BrandCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Deactivate Brand",
            value=(
                examples
                .BRAND_PARTIAL_UPDATE_EXAMPLE
            ),
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                BrandMutationResponseSerializer
            ),
            description=(
                "Brand updated successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brand Updated",
                    value=(
                        responses
                        .BrandUpdateAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
            examples=[
                OpenApiExample(
                    name="Duplicate Brand",
                    value=(
                        responses
                        .BrandDuplicateName
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    name=(
                        "Authentication Required"
                    ),
                    value=(
                        responses
                        .BrandAuthenticationRequired
                    ),
                    response_only=True,
                ),
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
                        .BrandPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
            examples=[
                OpenApiExample(
                    name="Brand Not Found",
                    value=(
                        responses
                        .BrandNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Brand Delete
# =========================================================


brand_delete_view_schema = extend_schema(
    tags=[
        "Brands",
    ],
    operation_id="brand_delete",
    summary="Delete Brand",
    description=(
        "Deletes a brand. "
        "Only admin users can use this endpoint. "
        "If another protected object depends on "
        "the brand, it cannot be deleted."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                BrandDeleteResponseSerializer
            ),
            description=(
                "Brand deleted successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Brand Deleted",
                    value=(
                        responses
                        .BrandDeleteAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    name=(
                        "Authentication Required"
                    ),
                    value=(
                        responses
                        .BrandAuthenticationRequired
                    ),
                    response_only=True,
                ),
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
                        .BrandPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
            examples=[
                OpenApiExample(
                    name="Brand Not Found",
                    value=(
                        responses
                        .BrandNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
        409: OpenApiResponse(
            response=(
                BrandDeleteProtectedResponseSerializer
            ),
            description=(
                "Brand cannot be deleted because "
                "another object depends on it."
            ),
            examples=[
                OpenApiExample(
                    name="Protected Brand",
                    value=(
                        responses
                        .BrandDeleteProtected
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)