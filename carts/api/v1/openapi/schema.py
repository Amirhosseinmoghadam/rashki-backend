from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from . import examples


# =========================================================
# Cart List View Schema
# =========================================================

cart_list_view_schema = extend_schema(
    tags=["Cart"],
    operation_id="get_user_cart",
    summary="Get User Cart",
    description=(
        "Retrieves the authenticated user's shopping cart with all items, "
        "quantities, and calculated totals."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Cart Retrieved Successfully",
                    value=examples.CartListViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
    },
)


# =========================================================
# Add to Cart View Schema
# =========================================================

add_to_cart_view_schema = extend_schema(
    tags=["Cart"],
    operation_id="add_to_cart",
    summary="Add Item to Cart",
    description=(
        "Adds a product variant to the user's shopping cart. "
        "If the variant already exists in the cart, the quantity will be increased. "
        "The variant must be active and have stock available."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "variant_id": {
                    "type": "integer",
                    "description": "Product variant ID to add to cart.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to add (default: 1).",
                    "default": 1,
                },
            },
            "required": ["variant_id"],
        }
    },
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.AddToCartViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Item added to cart successfully.",
            examples=[
                OpenApiExample(
                    name="Item Added Successfully",
                    value=examples.AddToCartViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error (invalid variant, insufficient stock, etc.).",
            examples=[
                OpenApiExample(
                    name="Validation Error",
                    value=examples.ValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Variant not found.",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=examples.NotFoundError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Update Cart Item View Schema
# =========================================================

update_cart_item_view_schema = extend_schema(
    tags=["Cart"],
    operation_id="update_cart_item",
    summary="Update Cart Item Quantity",
    description=(
        "Updates the quantity of a specific item in the user's cart. "
        "The new quantity must be at least 1."
    ),
    parameters=[],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "quantity": {
                    "type": "integer",
                    "description": "New quantity for the cart item.",
                    "minimum": 1,
                },
            },
            "required": ["quantity"],
        }
    },
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.UpdateCartItemViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart item quantity updated successfully.",
            examples=[
                OpenApiExample(
                    name="Quantity Updated Successfully",
                    value=examples.UpdateCartItemViewSuccess,
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
                    value=examples.ValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart item not found.",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=examples.NotFoundError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Remove Cart Item View Schema
# =========================================================

remove_cart_item_view_schema = extend_schema(
    tags=["Cart"],
    operation_id="remove_cart_item",
    summary="Remove Item from Cart",
    description="Removes a specific item from the user's shopping cart.",
    parameters=[],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Item removed from cart successfully.",
            examples=[
                OpenApiExample(
                    name="Item Removed Successfully",
                    value=examples.RemoveCartItemViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart item not found.",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=examples.NotFoundError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Clear Cart View Schema
# =========================================================

clear_cart_view_schema = extend_schema(
    tags=["Cart"],
    operation_id="clear_cart",
    summary="Clear Cart",
    description="Removes all items from the user's shopping cart.",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart cleared successfully.",
            examples=[
                OpenApiExample(
                    name="Cart Cleared Successfully",
                    value=examples.ClearCartViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Cart not found.",
            examples=[
                OpenApiExample(
                    name="Not Found",
                    value=examples.NotFoundError,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)
