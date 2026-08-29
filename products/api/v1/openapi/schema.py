# from drf_spectacular.utils import (
#     extend_schema,
#     OpenApiExample,
#     OpenApiResponse,
#     OpenApiTypes,
#     extend_schema_view,
# )
#
# from . import examples, responses
# from ..serializers import ProductImageSerializer, AttributeGroupSerializer, AttributeSerializer, \
#     AttributeValueSerializer, ProductVariantSerializer, ProductMotorcycleCompatibilitySerializer
#
# # =========================================================
# # Product Schemas
# # =========================================================
#
# product_list_create_schema = extend_schema(
#     tags=["Products"],
#     operation_id="product_list_create",
#     summary="List or Create Products",
#     description=(
#         "GET: Returns a list of all active products.\n\n"
#         "POST: Creates a new product (requires authentication)."
#     ),
#     responses={
#         200: OpenApiResponse(
#             response=OpenApiTypes.OBJECT,
#             description="List of products retrieved successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product List Success",
#                     value=responses.ProductListSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         201: OpenApiResponse(
#             response=OpenApiTypes.OBJECT,
#             description="Product created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product Create Success",
#                     value=responses.ProductCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         400: OpenApiResponse(
#             response=OpenApiTypes.OBJECT,
#             description="Validation error.",
#             examples=[
#                 OpenApiExample(
#                     name="Validation Error",
#                     value=responses.ProductValidationError,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# product_retrieve_update_destroy_schema = extend_schema(
#     tags=["Products"],
#     operation_id="product_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Product",
#     description=(
#         "GET: Returns a single product by slug.\n\n"
#         "PUT/PATCH: Updates a product (requires authentication).\n\n"
#         "DELETE: Deletes a product (requires authentication)."
#     ),
#     responses={
#         200: OpenApiResponse(
#             response=OpenApiTypes.OBJECT,
#             description="Product retrieved/updated successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product Detail Success",
#                     value=responses.ProductDetailSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         404: OpenApiResponse(
#             response=OpenApiTypes.OBJECT,
#             description="Product not found.",
#             examples=[
#                 OpenApiExample(
#                     name="Not Found",
#                     value=responses.ProductNotFoundError,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# # =========================================================
# # Product Image Schemas
# # =========================================================
#
# product_image_list_create_schema = extend_schema(
#     tags=["Product Images"],
#     operation_id="product_image_list_create",
#     summary="List or Create Product Images",
#     description=(
#         "GET: Returns a list of all images for a product.\n\n"
#         "POST: Creates a new product image (requires authentication)."
#     ),
#     responses={
#         200: OpenApiResponse(
#             response=ProductImageSerializer(many=True),
#             description="List of product images retrieved successfully.",
#         ),
#         201: OpenApiResponse(
#             response=ProductImageSerializer,
#             description="Product image created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product Image Create Success",
#                     value=responses.ProductImageCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
# product_image_retrieve_update_destroy_schema = extend_schema(
#     tags=["Product Images"],
#     operation_id="product_image_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Product Image",
#     responses={
#         200: OpenApiResponse(
#             description="Product image retrieved/updated successfully.",
#         ),
#         404: OpenApiResponse(
#             description="Product image not found.",
#         ),
#     },
# )
#
#
# # =========================================================
# # Attribute Group Schemas
# # =========================================================
#
# attribute_group_list_create_schema = extend_schema(
#     tags=["Attribute Groups"],
#     operation_id="attribute_group_list_create",
#     summary="List or Create Attribute Groups",
#     responses={
#         200: OpenApiResponse(
#             response=AttributeGroupSerializer(many=True),
#             description="List of attribute groups retrieved successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Attribute Group List Success",
#                     value=responses.AttributeGroupListSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         201: OpenApiResponse(
#             response=AttributeGroupSerializer,
#             description="Attribute group created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Attribute Group Create Success",
#                     value=responses.AttributeGroupCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# attribute_group_retrieve_update_destroy_schema = extend_schema(
#     tags=["Attribute Groups"],
#     operation_id="attribute_group_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Attribute Group",
#     responses={
#         200: OpenApiResponse(
#             response=AttributeGroupSerializer,
#             description="Attribute group retrieved/updated successfully.",
#         ),
#         404: OpenApiResponse(
#             description="Attribute group not found.",
#         ),
#     },
# )
#
# # =========================================================
# # Attribute Schemas
# # =========================================================
#
# attribute_list_create_schema = extend_schema(
#     tags=["Attributes"],
#     operation_id="attribute_list_create",
#     summary="List or Create Attributes",
#     responses={
#         200: OpenApiResponse(
#             response=AttributeSerializer(many=True),
#             description="List of attributes retrieved successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Attribute List Success",
#                     value=responses.AttributeListSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         201: OpenApiResponse(
#             response=AttributeSerializer,
#             description="Attribute created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Attribute Create Success",
#                     value=responses.AttributeCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# attribute_retrieve_update_destroy_schema = extend_schema(
#     tags=["Attributes"],
#     operation_id="attribute_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Attribute",
#     responses={
#         200: OpenApiResponse(description="Attribute retrieved/updated successfully."),
#         404: OpenApiResponse(description="Attribute not found."),
#     },
# )
#
#
# # =========================================================
# # Attribute Value Schemas
# # =========================================================
#
# attribute_value_list_create_schema = extend_schema(
#     tags=["Attribute Values"],
#     operation_id="attribute_value_list_create",
#     summary="List or Create Attribute Values",
#     responses={
#         200: OpenApiResponse(
#             response=AttributeValueSerializer(many=True),
#             description="List of attribute values retrieved successfully.",
#         ),
#         201: OpenApiResponse(
#             response=AttributeValueSerializer,
#             description="Attribute value created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Attribute Value Create Success",
#                     value=responses.AttributeValueCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# attribute_value_retrieve_update_destroy_schema = extend_schema(
#     tags=["Attribute Values"],
#     operation_id="attribute_value_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Attribute Value",
#     responses={
#         200: OpenApiResponse(description="Attribute value retrieved/updated successfully."),
#         404: OpenApiResponse(description="Attribute value not found."),
#     },
# )
#
#
# # =========================================================
# # Product Variant Schemas
# # =========================================================
#
# product_variant_list_create_schema = extend_schema(
#     tags=["Product Variants"],
#     operation_id="product_variant_list_create",
#     summary="List or Create Product Variants",
#     responses={
#         200: OpenApiResponse(
#             response=ProductVariantSerializer(many=True),
#             description="List of product variants retrieved successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product Variant List Success",
#                     value=responses.ProductVariantListSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#         201: OpenApiResponse(
#             response=ProductVariantSerializer,
#             description="Product variant created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Product Variant Create Success",
#                     value=responses.ProductVariantCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# product_variant_retrieve_update_destroy_schema = extend_schema(
#     tags=["Product Variants"],
#     operation_id="product_variant_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Product Variant",
#     responses={
#         200: OpenApiResponse(description="Product variant retrieved/updated successfully."),
#         404: OpenApiResponse(description="Product variant not found."),
#     },
# )
#
#
# # =========================================================
# # Product Motorcycle Compatibility Schemas
# # =========================================================
#
# product_motorcycle_compatibility_list_create_schema = extend_schema(
#     tags=["Product Motorcycle Compatibility"],
#     operation_id="product_motorcycle_compatibility_list_create",
#     summary="List or Create Motorcycle Compatibilities",
#     responses={
#         200: OpenApiResponse(
#             response=ProductMotorcycleCompatibilitySerializer(many=True),
#             description="List of motorcycle compatibilities retrieved successfully.",
#         ),
#         201: OpenApiResponse(
#             response=ProductMotorcycleCompatibilitySerializer,
#             description="Motorcycle compatibility created successfully.",
#             examples=[
#                 OpenApiExample(
#                     name="Motorcycle Compatibility Create Success",
#                     value=responses.ProductMotorcycleCompatibilityCreateSuccess,
#                     media_type="application/json",
#                     response_only=True,
#                 ),
#             ],
#         ),
#     },
# )
#
#
# product_motorcycle_compatibility_retrieve_update_destroy_schema = extend_schema(
#     tags=["Product Motorcycle Compatibility"],
#     operation_id="product_motorcycle_compatibility_retrieve_update_destroy",
#     summary="Retrieve, Update, or Delete Motorcycle Compatibility",
#     responses={
#         200: OpenApiResponse(description="Motorcycle compatibility retrieved/updated successfully."),
#         404: OpenApiResponse(description="Motorcycle compatibility not found."),
#     },
# )

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from . import examples, responses

from ..serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ProductImageCreateSerializer,
    AttributeGroupSerializer,
    AttributeGroupCreateUpdateSerializer,
    AttributeSerializer,
    AttributeCreateUpdateSerializer,
    AttributeValueSerializer,
    AttributeValueCreateUpdateSerializer,
    ProductVariantSerializer,
    ProductVariantCreateUpdateSerializer,
    ProductVariantDetailSerializer,
    ProductMotorcycleCompatibilitySerializer,
    ProductMotorcycleCompatibilityCreateUpdateSerializer,
)

# =========================================================
# Product
# =========================================================

product_list_schema = extend_schema(
    tags=["Products"],
    operation_id="product_list",
    summary="List Products",
    description=("Returns a list of all active products."),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="List of products retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Product List Success",
                    value=responses.ProductListSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


product_create_schema = extend_schema(
    tags=["Products"],
    operation_id="product_create",
    summary="Create Product",
    description=("Creates a new product. " "Authentication is required."),
    request=ProductCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product created successfully.",
            examples=[
                OpenApiExample(
                    name="Product Create Success",
                    value=responses.ProductCreateSuccess,
                    media_type="application/json",
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
                    value=responses.ProductValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


product_retrieve_schema = extend_schema(
    tags=["Products"],
    operation_id="product_retrieve",
    summary="Retrieve Product",
    description=("Returns a single product by slug."),
    responses={
        200: OpenApiResponse(
            response=ProductDetailSerializer,
            description="Product retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=responses.ProductNotFoundError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


product_update_schema = extend_schema(
    tags=["Products"],
    operation_id="product_update",
    summary="Update Product",
    description=("Completely updates a product. " "Authentication is required."),
    request=ProductCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_partial_update_schema = extend_schema(
    tags=["Products"],
    operation_id="product_partial_update",
    summary="Partially Update Product",
    description=("Partially updates a product. " "Only submitted fields are updated."),
    request=ProductCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_delete_schema = extend_schema(
    tags=["Products"],
    operation_id="product_delete",
    summary="Delete Product",
    description=("Deletes a product by slug. " "Authentication is required."),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


# =========================================================
# Product Images
# =========================================================

product_image_list_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_list",
    summary="List Product Images",
    description=("Returns all images belonging to a product."),
    responses={
        200: OpenApiResponse(
            response=ProductImageSerializer(many=True),
            description="Product images retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_image_create_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_create",
    summary="Create Product Image",
    description=("Creates a new image for a product."),
    request=ProductImageCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image created successfully.",
            examples=[
                OpenApiExample(
                    name="Product Image Create Success",
                    value=responses.ProductImageCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_image_retrieve_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_retrieve",
    summary="Retrieve Product Image",
    description="Returns a single product image.",
    responses={
        200: OpenApiResponse(
            response=ProductImageSerializer,
            description="Product image retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image not found.",
        ),
    },
)


product_image_update_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_update",
    summary="Update Product Image",
    description="Completely updates a product image.",
    request=ProductImageCreateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image not found.",
        ),
    },
)


product_image_partial_update_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_partial_update",
    summary="Partially Update Product Image",
    description="Partially updates a product image.",
    request=ProductImageCreateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image not found.",
        ),
    },
)


product_image_delete_schema = extend_schema(
    tags=["Product Images"],
    operation_id="product_image_delete",
    summary="Delete Product Image",
    description="Deletes a product image.",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product image not found.",
        ),
    },
)


# =========================================================
# Attribute Groups
# =========================================================

attribute_group_list_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_list",
    summary="List Attribute Groups",
    description="Returns all active attribute groups.",
    responses={
        200: OpenApiResponse(
            response=AttributeGroupSerializer(many=True),
            description="Attribute groups retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Attribute Group List Success",
                    value=responses.AttributeGroupListSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


attribute_group_create_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_create",
    summary="Create Attribute Group",
    request=AttributeGroupCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group created successfully.",
            examples=[
                OpenApiExample(
                    name="Attribute Group Create Success",
                    value=responses.AttributeGroupCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
    },
)


attribute_group_retrieve_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_retrieve",
    summary="Retrieve Attribute Group",
    responses={
        200: OpenApiResponse(
            response=AttributeGroupSerializer,
            description="Attribute group retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group not found.",
        ),
    },
)


attribute_group_update_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_update",
    summary="Update Attribute Group",
    request=AttributeGroupCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group not found.",
        ),
    },
)


attribute_group_partial_update_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_partial_update",
    summary="Partially Update Attribute Group",
    request=AttributeGroupCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group not found.",
        ),
    },
)


attribute_group_delete_schema = extend_schema(
    tags=["Attribute Groups"],
    operation_id="attribute_group_delete",
    summary="Delete Attribute Group",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute group not found.",
        ),
    },
)


# =========================================================
# Attributes
# =========================================================

attribute_list_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_list",
    summary="List Attributes",
    description="Returns all active attributes.",
    responses={
        200: OpenApiResponse(
            response=AttributeSerializer(many=True),
            description="Attributes retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Attribute List Success",
                    value=responses.AttributeListSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


attribute_create_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_create",
    summary="Create Attribute",
    request=AttributeCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute created successfully.",
            examples=[
                OpenApiExample(
                    name="Attribute Create Success",
                    value=responses.AttributeCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
    },
)


attribute_retrieve_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_retrieve",
    summary="Retrieve Attribute",
    responses={
        200: OpenApiResponse(
            response=AttributeSerializer,
            description="Attribute retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute not found.",
        ),
    },
)


attribute_update_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_update",
    summary="Update Attribute",
    request=AttributeCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute not found.",
        ),
    },
)


attribute_partial_update_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_partial_update",
    summary="Partially Update Attribute",
    request=AttributeCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute not found.",
        ),
    },
)


attribute_delete_schema = extend_schema(
    tags=["Attributes"],
    operation_id="attribute_delete",
    summary="Delete Attribute",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute not found.",
        ),
    },
)


# =========================================================
# Attribute Values
# =========================================================

attribute_value_list_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_list",
    summary="List Attribute Values",
    responses={
        200: OpenApiResponse(
            response=AttributeValueSerializer(many=True),
            description="Attribute values retrieved successfully.",
        ),
    },
)


attribute_value_create_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_create",
    summary="Create Attribute Value",
    request=AttributeValueCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value created successfully.",
            examples=[
                OpenApiExample(
                    name="Attribute Value Create Success",
                    value=responses.AttributeValueCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
    },
)


attribute_value_retrieve_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_retrieve",
    summary="Retrieve Attribute Value",
    responses={
        200: OpenApiResponse(
            response=AttributeValueSerializer,
            description="Attribute value retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value not found.",
        ),
    },
)


attribute_value_update_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_update",
    summary="Update Attribute Value",
    request=AttributeValueCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value not found.",
        ),
    },
)


attribute_value_partial_update_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_partial_update",
    summary="Partially Update Attribute Value",
    request=AttributeValueCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value not found.",
        ),
    },
)


attribute_value_delete_schema = extend_schema(
    tags=["Attribute Values"],
    operation_id="attribute_value_delete",
    summary="Delete Attribute Value",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Attribute value not found.",
        ),
    },
)


# =========================================================
# Product Variants
# =========================================================

product_variant_list_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_list",
    summary="List Product Variants",
    description="Returns all variants belonging to a product.",
    responses={
        200: OpenApiResponse(
            response=ProductVariantSerializer(many=True),
            description="Product variants retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Product Variant List Success",
                    value=responses.ProductVariantListSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_variant_create_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_create",
    summary="Create Product Variant",
    request=ProductVariantCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant created successfully.",
            examples=[
                OpenApiExample(
                    name="Product Variant Create Success",
                    value=responses.ProductVariantCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_variant_retrieve_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_retrieve",
    summary="Retrieve Product Variant",
    responses={
        200: OpenApiResponse(
            response=ProductVariantDetailSerializer,
            description="Product variant retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant not found.",
        ),
    },
)


product_variant_update_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_update",
    summary="Update Product Variant",
    request=ProductVariantCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant not found.",
        ),
    },
)


product_variant_partial_update_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_partial_update",
    summary="Partially Update Product Variant",
    request=ProductVariantCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant partially updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant not found.",
        ),
    },
)


product_variant_delete_schema = extend_schema(
    tags=["Product Variants"],
    operation_id="product_variant_delete",
    summary="Delete Product Variant",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product variant not found.",
        ),
    },
)


# =========================================================
# Motorcycle Compatibility
# =========================================================

product_motorcycle_compatibility_list_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_list",
    summary="List Motorcycle Compatibilities",
    description=("Returns all motorcycle compatibilities " "for a product."),
    responses={
        200: OpenApiResponse(
            response=ProductMotorcycleCompatibilitySerializer(many=True),
            description="Motorcycle compatibilities retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_motorcycle_compatibility_create_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_create",
    summary="Create Motorcycle Compatibility",
    request=ProductMotorcycleCompatibilityCreateUpdateSerializer,
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility created successfully.",
            examples=[
                OpenApiExample(
                    name="Motorcycle Compatibility Create Success",
                    value=responses.ProductMotorcycleCompatibilityCreateSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Product not found.",
        ),
    },
)


product_motorcycle_compatibility_retrieve_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_retrieve",
    summary="Retrieve Motorcycle Compatibility",
    responses={
        200: OpenApiResponse(
            response=ProductMotorcycleCompatibilitySerializer,
            description="Motorcycle compatibility retrieved successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility not found.",
        ),
    },
)


product_motorcycle_compatibility_update_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_update",
    summary="Update Motorcycle Compatibility",
    request=ProductMotorcycleCompatibilityCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility updated successfully.",
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility not found.",
        ),
    },
)


product_motorcycle_compatibility_partial_update_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_partial_update",
    summary="Partially Update Motorcycle Compatibility",
    request=ProductMotorcycleCompatibilityCreateUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=("Motorcycle compatibility partially updated successfully."),
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility not found.",
        ),
    },
)


product_motorcycle_compatibility_delete_schema = extend_schema(
    tags=["Product Motorcycle Compatibility"],
    operation_id="product_motorcycle_compatibility_delete",
    summary="Delete Motorcycle Compatibility",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility deleted successfully.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Motorcycle compatibility not found.",
        ),
    },
)
