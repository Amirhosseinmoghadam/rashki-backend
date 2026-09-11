from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from products.api.v1.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ProductImageWriteSerializer,
    ProductAttributeReferenceSerializer,
)

from . import examples
from . import responses


# =========================================================
# Product Response Schemas
# =========================================================


ProductPaginationDataSerializer = inline_serializer(
    name="ProductPaginationData",
    fields={
        "count": serializers.IntegerField(),
        "next": serializers.URLField(
            allow_null=True
        ),
        "previous": serializers.URLField(
            allow_null=True
        ),
        "results": ProductListSerializer(
            many=True
        ),
    },
)


ProductListResponseSerializer = inline_serializer(
    name="ProductListResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProductPaginationDataSerializer,
    },
)


ProductDetailResponseSerializer = inline_serializer(
    name="ProductDetailResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProductDetailSerializer(),
    },
)


ProductMutationResponseSerializer = inline_serializer(
    name="ProductMutationResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProductDetailSerializer(),
    },
)


ProductDeleteResponseSerializer = inline_serializer(
    name="ProductDeleteResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True
        ),
    },
)


ProductDeleteProtectedResponseSerializer = inline_serializer(
    name="ProductDeleteProtectedResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True
        ),
    },
)


# =========================================================
# Product List
# =========================================================


product_list_view_schema = extend_schema(
    tags=["Products"],
    auth=[],
    operation_id="product_list",
    summary="List Products",
    description=(
        "Returns publicly visible active products.\n\n"
        "Supported filters:\n"
        "- category\n"
        "- brand\n"
        "- motorcycle\n"
        "- min_price / max_price (Toman)\n"
        "- in_stock\n"
        "- featured\n"
        "- search\n"
        "- ordering\n\n"
        "Dynamic product attributes can also be filtered "
        "using parameters such as:\n"
        "`attr_<attribute-slug>=value`\n"
        "`attr_<attribute-slug>_min=value`\n"
        "`attr_<attribute-slug>_max=value`."
    ),
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Category ID. Products from descendant "
                "categories are included."
            ),
        ),
        OpenApiParameter(
            name="brand",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Product brand ID.",
        ),
        OpenApiParameter(
            name="motorcycle",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Motorcycle model ID. Only compatible "
                "products are returned."
            ),
        ),
        OpenApiParameter(
            name="min_price",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Minimum product price in Toman.",
        ),
        OpenApiParameter(
            name="max_price",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Maximum product price in Toman.",
        ),
        OpenApiParameter(
            name="in_stock",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by stock availability.",
        ),
        OpenApiParameter(
            name="featured",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter featured products.",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Search by product name, SKU, OEM code, "
                "part number, barcode, keywords, brand, "
                "category or compatible motorcycle."
            ),
            examples=[
                OpenApiExample(
                    name="Part Number",
                    value="CPR6EA-9",
                ),
                OpenApiExample(
                    name="Motorcycle",
                    value="CG125",
                ),
            ],
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            enum=[
                "newest",
                "oldest",
                "price_asc",
                "price_desc",
                "name",
            ],
            description="Product ordering.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductListResponseSerializer,
            description="Products retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Products Retrieved",
                    value=responses.ProductListSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Invalid filter parameter.",
        ),
    },
)


# =========================================================
# Product Detail
# =========================================================


product_detail_view_schema = extend_schema(
    tags=["Products"],
    auth=[],
    operation_id="product_detail",
    summary="Get Product",
    description=(
        "Returns the public detail of an active product. "
        "Inactive or archived products are not exposed "
        "through this public endpoint."
    ),
    responses={
        200: OpenApiResponse(
            response=ProductDetailResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Retrieved",
                    value=responses.ProductDetailSuccess,
                    response_only=True,
                )
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Product Not Found",
                    value=responses.ProductNotFound,
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Product Create
# =========================================================


product_create_view_schema = extend_schema(
    tags=["Products"],
    operation_id="product_create",
    summary="Create Product",
    description=(
        "Creates a product. Admin permission is required. "
        "The slug and final Toman price are generated "
        "by the backend."
    ),
    request=ProductCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="USD Based Product",
            value=examples.PRODUCT_CREATE_USD_EXAMPLE,
            request_only=True,
        ),
        OpenApiExample(
            name="Fixed Toman Product",
            value=examples.PRODUCT_CREATE_FIXED_EXAMPLE,
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=ProductMutationResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Created",
                    value=responses.ProductCreateSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product validation error.",
            examples=[
                OpenApiExample(
                    name="Required Field",
                    value=responses.ProductValidationError,
                    response_only=True,
                ),
                OpenApiExample(
                    name="USD Price Required",
                    value=responses.ProductUSDPriceRequired,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Toman Price Required",
                    value=responses.ProductTomanPriceRequired,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Inactive Category",
                    value=responses.ProductInactiveCategory,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Inactive Brand",
                    value=responses.ProductInactiveBrand,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Attribute",
                    value=responses.ProductInvalidAttribute,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Required Attribute Missing",
                    value=responses.ProductMissingRequiredAttribute,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Pricing Error",
                    value=responses.ProductPricingError,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Authentication Required",
                    value=responses.AuthenticationRequired,
                    response_only=True,
                )
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=responses.PermissionDenied,
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Product Update
# =========================================================


product_update_view_schema = extend_schema(
    tags=["Products"],
    operation_id="product_update",
    summary="Update Product",
    description=(
        "Fully updates a product. "
        "Admin permission is required."
    ),
    request=ProductCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Update Product",
            value=examples.PRODUCT_UPDATE_EXAMPLE,
            request_only=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ProductMutationResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Updated",
                    value=responses.ProductUpdateSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Product Not Found",
                    value=responses.ProductNotFound,
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Product Partial Update
# =========================================================


product_partial_update_view_schema = extend_schema(
    tags=["Products"],
    operation_id="product_partial_update",
    summary="Partially Update Product",
    description=(
        "Updates only submitted product fields. "
        "If attributes, compatibilities or "
        "related_product_ids are omitted, their existing "
        "values remain unchanged."
    ),
    request=ProductCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Partial Update Product",
            value=examples.PRODUCT_PARTIAL_UPDATE_EXAMPLE,
            request_only=True,
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ProductMutationResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Updated",
                    value=responses.ProductUpdateSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Product Delete
# =========================================================


product_delete_view_schema = extend_schema(
    tags=["Products"],
    operation_id="product_delete",
    summary="Delete Product",
    description=(
        "Deletes a product if no protected object "
        "depends on it."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            response=ProductDeleteResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Deleted",
                    value=responses.ProductDeleteSuccess,
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        409: OpenApiResponse(
            response=ProductDeleteProtectedResponseSerializer,
            examples=[
                OpenApiExample(
                    name="Product Protected",
                    value=responses.ProductDeleteProtected,
                    response_only=True,
                )
            ],
        ),
    },
)


# =========================================================
# Product Image - List
# =========================================================


product_image_list_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_list",
    summary="List Product Images",
    description=(
        "Returns product images. "
        "Admin permission is required."
    ),
    responses={
        200: OpenApiResponse(
            response=ProductImageSerializer(many=True),
            examples=[
                OpenApiExample(
                    name="Product Images",
                    value=responses.ProductImageListSuccess,
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Product Image - Detail
# =========================================================


product_image_detail_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_detail",
    summary="Get Product Image",
    responses={
        200: OpenApiResponse(
            response=ProductImageSerializer,
            examples=[
                OpenApiExample(
                    name="Product Image",
                    value=responses.ProductImageSuccess,
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Product Image - Create
# =========================================================


product_image_create_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_create",
    summary="Upload Product Image",
    description=(
        "Uploads a product image. "
        "Use multipart/form-data. "
        "Each product can have at most 20 images."
    ),
    request=ProductImageWriteSerializer,
    examples=[
        OpenApiExample(
            name="Upload Product Image",
            value=examples.PRODUCT_IMAGE_CREATE_EXAMPLE,
            request_only=True,
        )
    ],
    responses={
        201: OpenApiResponse(
            response=ProductImageSerializer,
            examples=[
                OpenApiExample(
                    name="Image Created",
                    value=responses.ProductImageSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="Image Limit",
                    value=responses.ProductImageLimitError,
                    response_only=True,
                ),
                OpenApiExample(
                    name="Image Product Change",
                    value=responses.ProductImageMoveError,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Product Image - Update
# =========================================================


product_image_update_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_update",
    summary="Update Product Image",
    request=ProductImageWriteSerializer,
    examples=[
        OpenApiExample(
            name="Update Product Image",
            value=examples.PRODUCT_IMAGE_UPDATE_EXAMPLE,
            request_only=True,
        )
    ],
    responses={
        200: ProductImageSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Product Image - Partial Update
# =========================================================


product_image_partial_update_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_partial_update",
    summary="Partially Update Product Image",
    request=ProductImageWriteSerializer,
    examples=[
        OpenApiExample(
            name="Partial Update Product Image",
            value=examples.PRODUCT_IMAGE_PARTIAL_UPDATE_EXAMPLE,
            request_only=True,
        )
    ],
    responses={
        200: ProductImageSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    },
)


# =========================================================
# Product Image - Delete
# =========================================================


product_image_delete_view_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_delete",
    summary="Delete Product Image",
    description=(
        "Deletes an image. If the primary image is deleted, "
        "the next available image becomes primary."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Image deleted successfully."
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT
        ),
    },
)


# =========================================================
# Product Attribute - List
# =========================================================


product_attribute_list_view_schema = extend_schema(
    tags=["Product Attributes"],
    auth=[],
    operation_id="product_attribute_list",
    summary="List Product Attributes",
    description=(
        "Returns active product attributes. "
        "When category is supplied, attributes inherited "
        "from the category and its ancestors are returned."
    ),
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Category ID.",
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ProductAttributeReferenceSerializer(
                many=True
            ),
            examples=[
                OpenApiExample(
                    name="Product Attributes",
                    value=responses.ProductAttributeListSuccess,
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


# =========================================================
# Product Attribute - Detail
# =========================================================


product_attribute_detail_view_schema = extend_schema(
    tags=["Product Attributes"],
    auth=[],
    operation_id="product_attribute_detail",
    summary="Get Product Attribute",
    responses={
        200: ProductAttributeReferenceSerializer,
        404: OpenApiTypes.OBJECT,
    },
)