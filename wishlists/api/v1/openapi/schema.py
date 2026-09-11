from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from wishlists.api.v1.serializers import (
    WishlistItemSerializer,
)

from . import responses


# =========================================================
# Pagination
# =========================================================


WishlistPaginationDataSerializer = (
    inline_serializer(
        name="WishlistPaginationData",
        fields={
            "count": (
                serializers.IntegerField()
            ),
            "next": serializers.URLField(
                allow_null=True
            ),
            "previous": serializers.URLField(
                allow_null=True
            ),
            "results": (
                WishlistItemSerializer(
                    many=True
                )
            ),
        },
    )
)


# =========================================================
# List Response
# =========================================================


WishlistListResponseSerializer = (
    inline_serializer(
        name="WishlistListResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                WishlistPaginationDataSerializer
            ),
        },
    )
)


# =========================================================
# Mutation Response
# =========================================================


WishlistMutationResponseSerializer = (
    inline_serializer(
        name="WishlistMutationResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                WishlistItemSerializer()
            ),
        },
    )
)


# =========================================================
# Delete Response
# =========================================================


WishlistDeleteResponseSerializer = (
    inline_serializer(
        name="WishlistDeleteResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": serializers.JSONField(
                allow_null=True
            ),
        },
    )
)


# =========================================================
# Error Response
# =========================================================


WishlistErrorResponseSerializer = (
    inline_serializer(
        name="WishlistErrorResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "errors": serializers.JSONField(
                allow_null=True
            ),
        },
    )
)


# =========================================================
# Product IDs Response
# =========================================================


WishlistProductIdsResponseSerializer = (
    inline_serializer(
        name="WishlistProductIdsResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "count": (
                serializers.IntegerField()
            ),
            "data": serializers.ListField(
                child=(
                    serializers.IntegerField()
                )
            ),
        },
    )
)


# =========================================================
# Wishlist List
# =========================================================


wishlist_list_view_schema = extend_schema(
    tags=[
        "Wishlist",
    ],
    operation_id="wishlist_list",
    summary="Get Wishlist",
    description=(
        "Returns the authenticated user's "
        "wishlist. Only currently public products "
        "are included."
    ),
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description="Page number.",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.QUERY
            ),
            required=False,
            description=(
                "Number of wishlist items "
                "per page. Maximum is 100."
            ),
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                WishlistListResponseSerializer
            ),
            description=(
                "Wishlist retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Wishlist",
                    value=(
                        responses
                        .WishlistListSuccess
                    ),
                    response_only=True,
                )
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
                        .AuthenticationRequired
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Add Wishlist Item
# =========================================================


wishlist_add_view_schema = extend_schema(
    tags=[
        "Wishlist",
    ],
    operation_id="wishlist_add",
    summary="Add Product To Wishlist",
    description=(
        "Adds a public product to the authenticated "
        "user's wishlist. Repeating the same request "
        "is safe and does not create duplicates."
    ),
    request=None,
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.PATH
            ),
            required=True,
            description="Product ID.",
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                WishlistMutationResponseSerializer
            ),
            description=(
                "Product added to wishlist."
            ),
            examples=[
                OpenApiExample(
                    name="Added",
                    value=(
                        responses
                        .WishlistAddSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        200: OpenApiResponse(
            response=(
                WishlistMutationResponseSerializer
            ),
            description=(
                "Product was already in wishlist."
            ),
            examples=[
                OpenApiExample(
                    name="Already Exists",
                    value=(
                        responses
                        .WishlistAlreadyExists
                    ),
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=(
                WishlistErrorResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Product Not Found",
                    value=(
                        responses
                        .WishlistProductNotFound
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Remove Wishlist Item
# =========================================================


wishlist_remove_view_schema = extend_schema(
    tags=[
        "Wishlist",
    ],
    operation_id="wishlist_remove",
    summary="Remove Product From Wishlist",
    description=(
        "Removes a product from the authenticated "
        "user's wishlist."
    ),
    request=None,
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=OpenApiTypes.INT,
            location=(
                OpenApiParameter.PATH
            ),
            required=True,
            description="Product ID.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=(
                WishlistDeleteResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Removed",
                    value=(
                        responses
                        .WishlistRemoveSuccess
                    ),
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=(
                WishlistErrorResponseSerializer
            ),
            examples=[
                OpenApiExample(
                    name="Not In Wishlist",
                    value=(
                        responses
                        .WishlistItemNotFound
                    ),
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Wishlist Product IDs
# =========================================================


wishlist_product_ids_view_schema = (
    extend_schema(
        tags=[
            "Wishlist",
        ],
        operation_id=(
            "wishlist_product_ids"
        ),
        summary="Get Wishlist Product IDs",
        description=(
            "Returns only product IDs in the "
            "authenticated user's wishlist. "
            "Useful for rendering wishlist icons "
            "on product cards without loading "
            "the full wishlist."
        ),
        responses={
            200: OpenApiResponse(
                response=(
                    WishlistProductIdsResponseSerializer
                ),
                examples=[
                    OpenApiExample(
                        name="Product IDs",
                        value=(
                            responses
                            .WishlistProductIdsSuccess
                        ),
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
            ),
        },
    )
)