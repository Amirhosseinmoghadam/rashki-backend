from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    inline_serializer,
)

from categories.api.v1.serializers import (
    CategorySerializer,
    CategoryDetailSerializer,
    CategoryCreateUpdateSerializer,
    CategoryTreeSerializer,
)
from . import examples
from . import responses

# =========================================================
# Category Tree Response
# =========================================================


CategoryTreeResponseSerializer = inline_serializer(
    name="CategoryTreeResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": CategoryTreeSerializer(
            many=True,
        ),
    },
)
# =========================================================
# Reusable Serializers
# =========================================================


CategoryListResponseSerializer = inline_serializer(
    name="CategoryListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "count": serializers.IntegerField(),
        "data": CategorySerializer(
            many=True,
        ),
    },
)


CategoryDetailResponseSerializer = inline_serializer(
    name="CategoryDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": CategoryDetailSerializer(),
    },
)


CategoryMutationResponseSerializer = inline_serializer(
    name="CategoryMutationResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": CategoryDetailSerializer(),
    },
)


CategoryDeleteResponseSerializer = inline_serializer(
    name="CategoryDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True,
        ),
    },
)


CategoryDeleteProtectedResponseSerializer = (
    inline_serializer(
        name="CategoryDeleteProtectedResponse",
        fields={
            "success": serializers.BooleanField(),
            "message": serializers.CharField(),
            "errors": serializers.JSONField(
                allow_null=True,
            ),
        },
    )
)


# =========================================================
# Tree Schema
# =========================================================
#
# Recursive serializers are inconvenient to represent
# directly with DRF serializers, therefore the recursive
# OpenAPI schema is declared explicitly here.
# =========================================================




# =========================================================
# Category List
# =========================================================


category_list_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_list",
    summary="List Categories",
    description=(
        "Returns all active categories. "
        "The endpoint is public and can be used "
        "for storefront category navigation. "
        "Categories can be filtered by parent "
        "or searched by name and description."
    ),
    parameters=[
        OpenApiParameter(
            name="parent",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter categories by parent ID. "
                'Use "root" to return only '
                "top-level categories."
            ),
            examples=[
                OpenApiExample(
                    name="Parent ID",
                    value="1",
                ),
                OpenApiExample(
                    name="Root Categories",
                    value="root",
                ),
            ],
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Search active categories by "
                "name or description."
            ),
            examples=[
                OpenApiExample(
                    name="Search Example",
                    value="ترمز",
                ),
            ],
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=CategoryListResponseSerializer,
            description=(
                "Categories retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Categories Retrieved "
                        "Successfully"
                    ),
                    value=(
                        responses
                        .CategoryListAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Detail
# =========================================================


category_detail_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_detail",
    summary="Get Category",
    description=(
        "Returns a single active category. "
        "The response contains basic information "
        "about its parent and active children."
    ),
    responses={
        200: OpenApiResponse(
            response=(
                CategoryDetailResponseSerializer
            ),
            description=(
                "Category retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Retrieved",
                    value=(
                        responses
                        .CategoryDetailAPIViewSuccess
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Category not found.",
            examples=[
                OpenApiExample(
                    name="Category Not Found",
                    value=(
                        responses
                        .CategoryNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Create
# =========================================================


category_create_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_create",
    summary="Create Category",
    description=(
        "Creates a new category. "
        "Only admin users can use this endpoint. "
        "The slug is generated automatically "
        "from the category name and cannot be "
        "submitted manually."
    ),
    request=CategoryCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Create Category",
            value=examples.CATEGORY_CREATE_EXAMPLE,
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                CategoryMutationResponseSerializer
            ),
            description=(
                "Category created successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Created",
                    value=(
                        responses
                        .CategoryCreateAPIViewSuccess
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
                        .CategoryValidationError
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Image",
                    value=(
                        responses
                        .CategoryInvalidImage
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
                    name="Authentication Required",
                    value=(
                        responses
                        .CategoryAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Authenticated user is not an admin."
            ),
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .CategoryPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Update
# =========================================================


category_update_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_update",
    summary="Update Category",
    description=(
        "Fully updates an existing category. "
        "Only admin users can use this endpoint. "
        "The category slug is read-only and remains "
        "unchanged when the category name changes."
    ),
    request=CategoryCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Update Category",
            value=examples.CATEGORY_UPDATE_EXAMPLE,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                CategoryMutationResponseSerializer
            ),
            description=(
                "Category updated successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Updated",
                    value=(
                        responses
                        .CategoryUpdateAPIViewSuccess
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
                        .CategoryValidationError
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Parent",
                    value=(
                        responses
                        .CategoryInvalidParent
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Circular Parent",
                    value=(
                        responses
                        .CategoryCircularParent
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
                    name="Authentication Required",
                    value=(
                        responses
                        .CategoryAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Admin permission required.",
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .CategoryPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Category not found.",
            examples=[
                OpenApiExample(
                    name="Category Not Found",
                    value=(
                        responses
                        .CategoryNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Partial Update
# =========================================================


category_partial_update_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_partial_update",
    summary="Partially Update Category",
    description=(
        "Partially updates an existing category. "
        "Only the fields that need to be changed "
        "should be submitted. "
        "The slug cannot be changed."
    ),
    request=CategoryCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Partial Update",
            value={
                "description": (
                    "انواع قطعات سیستم ترمز "
                    "موتورسیکلت."
                ),
                "is_active": True,
            },
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                CategoryMutationResponseSerializer
            ),
            description=(
                "Category updated successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Updated",
                    value=(
                        responses
                        .CategoryUpdateAPIViewSuccess
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
                    name="Invalid Parent",
                    value=(
                        responses
                        .CategoryInvalidParent
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Circular Parent",
                    value=(
                        responses
                        .CategoryCircularParent
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
                    name="Authentication Required",
                    value=(
                        responses
                        .CategoryAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Admin permission required.",
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .CategoryPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Category not found.",
            examples=[
                OpenApiExample(
                    name="Category Not Found",
                    value=(
                        responses
                        .CategoryNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Delete
# =========================================================


category_delete_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_delete",
    summary="Delete Category",
    description=(
        "Deletes a category. "
        "Only admin users can use this endpoint. "
        "If another protected object depends on the "
        "category, the category cannot be deleted."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                CategoryDeleteResponseSerializer
            ),
            description=(
                "Category deleted successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Deleted",
                    value=(
                        responses
                        .CategoryDeleteAPIViewSuccess
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
                    name="Authentication Required",
                    value=(
                        responses
                        .CategoryAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Admin permission required.",
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .CategoryPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Category not found.",
            examples=[
                OpenApiExample(
                    name="Category Not Found",
                    value=(
                        responses
                        .CategoryNotFound
                    ),
                    response_only=True,
                ),
            ],
        ),
        409: OpenApiResponse(
            response=(
                CategoryDeleteProtectedResponseSerializer
            ),
            description=(
                "Category cannot be deleted because "
                "another object depends on it."
            ),
            examples=[
                OpenApiExample(
                    name="Protected Category",
                    value=(
                        responses
                        .CategoryDeleteProtected
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Category Tree
# =========================================================


category_tree_view_schema = extend_schema(
    tags=[
        "Categories",
    ],
    operation_id="category_tree",
    summary="Get Category Tree",
    description=(
        "Returns all publicly visible categories "
        "as a hierarchical tree. "
        "Only active categories whose full parent "
        "chain is active are included."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            response=(
                CategoryTreeResponseSerializer
            ),
            description=(
                "Category tree retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Category Tree",
                    value=(
                        responses
                        .CategoryTreeAPIViewSuccess
                    ),
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)