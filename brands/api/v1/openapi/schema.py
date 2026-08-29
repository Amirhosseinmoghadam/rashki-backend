"""
OpenAPI Schema definitions for Brands API
"""

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from brands.api.v1.serializers import (
    BrandSerializer,
    BrandListSerializer,
    BrandCreateUpdateSerializer,
)

# =========================================================
# Brand List - GET
# =========================================================

brand_list_schema = extend_schema(
    operation_id="brands_list",
    summary="List Brands",
    description="Get a list of all active brands.",
    responses={
        200: OpenApiResponse(
            response=BrandListSerializer(many=True),
            description="List of active brands.",
            examples=[
                OpenApiExample(
                    "Successful Response",
                    value=[
                        {
                            "id": 1,
                            "name": "Rolex",
                            "slug": "rolex",
                            "logo": "https://example.com/media/brands/rolex.png",
                            "description": "Swiss luxury watch brand.",
                            "is_active": True,
                        },
                        {
                            "id": 2,
                            "name": "Omega",
                            "slug": "omega",
                            "logo": "https://example.com/media/brands/omega.png",
                            "description": "Swiss watch manufacturer.",
                            "is_active": True,
                        },
                    ],
                ),
            ],
        ),
    },
    tags=["Brands"],
)


# =========================================================
# Brand Create - POST
# =========================================================

brand_create_schema = extend_schema(
    operation_id="brands_create",
    summary="Create Brand",
    description="Create a new brand. Requires staff permissions.",
    request=BrandCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=BrandCreateUpdateSerializer,
            description="Brand created successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
            examples=[
                OpenApiExample(
                    "Validation Error",
                    value={"name": ["This field is required."]},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    "Authentication Error",
                    value={"detail": "Authentication credentials were not provided."},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Permission denied.",
            examples=[
                OpenApiExample(
                    "Permission Error",
                    value={"detail": ("You do not have permission to create brands.")},
                ),
            ],
        ),
    },
    tags=["Brands"],
)


# =========================================================
# Brand Detail - GET
# =========================================================

brand_detail_schema = extend_schema(
    operation_id="brand_detail",
    summary="Get Brand",
    description="Get details of a specific brand by ID or slug.",
    responses={
        200: OpenApiResponse(
            response=BrandSerializer,
            description="Brand details.",
            examples=[
                OpenApiExample(
                    "Successful Response",
                    value={
                        "id": 1,
                        "name": "Rolex",
                        "slug": "rolex",
                        "logo": ("https://example.com/media/brands/rolex.png"),
                        "description": ("Swiss luxury watch brand."),
                        "website": "https://www.rolex.com/",
                        "is_active": True,
                        "created_at": "2026-08-29T12:00:00Z",
                        "updated_at": "2026-08-29T12:00:00Z",
                    },
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
            examples=[
                OpenApiExample(
                    "Not Found",
                    value={"detail": "Not found."},
                ),
            ],
        ),
    },
    tags=["Brands"],
)


# =========================================================
# Brand Update - PUT
# =========================================================

brand_update_schema = extend_schema(
    operation_id="brand_update",
    summary="Update Brand",
    description="Update an existing brand. Requires staff permissions.",
    request=BrandCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=BrandSerializer,
            description="Brand updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Permission denied.",
            examples=[
                OpenApiExample(
                    "Permission Error",
                    value={"detail": ("You do not have permission to update brands.")},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
        ),
    },
    tags=["Brands"],
)


# =========================================================
# Brand Delete - DELETE
# =========================================================

brand_delete_schema = extend_schema(
    operation_id="brand_delete",
    summary="Delete Brand",
    description="Delete a brand. Requires staff permissions.",
    responses={
        204: OpenApiResponse(
            response=None,
            description="Brand deleted successfully.",
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Permission denied.",
            examples=[
                OpenApiExample(
                    "Permission Error",
                    value={"detail": ("You do not have permission to delete brands.")},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Brand not found.",
        ),
    },
    tags=["Brands"],
)
