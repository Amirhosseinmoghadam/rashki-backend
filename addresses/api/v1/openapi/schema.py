from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema_view,
)


from . import examples, responses

from addresses.api.v1.serializers import (
    AddressSerializer,
    AddressCreateSerializer,
    AddressUpdateSerializer,
)

# =========================================================
# Address List
# =========================================================

address_list_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_list",
    summary="List User Addresses",
    description=(
        "Returns all addresses belonging to the authenticated user. "
        "Only addresses owned by the current user are returned. "
        "The default address is returned first."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="User addresses retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Addresses Retrieved Successfully",
                    value=responses.AddressListAPIViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Authentication credentials were not provided "
                "or are invalid."
            ),
            examples=[
                OpenApiExample(
                    name="Authentication Required",
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Address Create
# =========================================================

address_create_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_create",
    summary="Create User Address",
    description=(
        "Creates a new address for the authenticated user. "
        "The user is automatically assigned to the address. "
        "The first address of a user is automatically set as "
        "the default address."
    ),
    request=AddressCreateSerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.AddressCreateAPIViewExample,
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address created successfully.",
            examples=[
                OpenApiExample(
                    name="Address Created Successfully",
                    value=responses.AddressCreateAPIViewSuccess,
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
                    value=responses.AddressValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Mobile Number",
                    value=responses.AddressInvalidMobileNumber,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Phone Number",
                    value=responses.AddressInvalidPhoneNumber,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="City Province Mismatch",
                    value=responses.AddressCityProvinceMismatch,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Address Detail
# =========================================================

address_detail_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_detail",
    summary="Get User Address",
    description=(
        "Returns a single address belonging to the authenticated user. "
        "Users cannot access addresses belonging to other users."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Address Retrieved Successfully",
                    value=responses.AddressDetailAPIViewSuccess,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address not found.",
            examples=[
                OpenApiExample(
                    name="Address Not Found",
                    value=responses.AddressNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Address Update
# =========================================================

address_update_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_update",
    summary="Update User Address",
    description=(
        "Updates an existing address belonging to the authenticated user. "
        "The PUT method requires the complete address data."
    ),
    request=AddressUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.AddressUpdateAPIViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address updated successfully.",
            examples=[
                OpenApiExample(
                    name="Address Updated Successfully",
                    value=responses.AddressUpdateAPIViewSuccess,
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
                    value=responses.AddressValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="City Province Mismatch",
                    value=responses.AddressCityProvinceMismatch,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Cannot Unset Default Address",
                    value=responses.AddressCannotUnsetDefault,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address not found.",
            examples=[
                OpenApiExample(
                    name="Address Not Found",
                    value=responses.AddressNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Address Partial Update
# =========================================================

address_partial_update_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_partial_update",
    summary="Partially Update User Address",
    description=(
        "Partially updates an existing address. "
        "Only the fields that need to be changed "
        "should be provided."
    ),
    request=AddressUpdateSerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.AddressPartialUpdateAPIViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address updated successfully.",
            examples=[
                OpenApiExample(
                    name="Address Updated Successfully",
                    value=responses.AddressUpdateAPIViewSuccess,
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
                    value=responses.AddressValidationError,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="City Province Mismatch",
                    value=responses.AddressCityProvinceMismatch,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Cannot Unset Default Address",
                    value=responses.AddressCannotUnsetDefault,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address not found.",
            examples=[
                OpenApiExample(
                    name="Address Not Found",
                    value=responses.AddressNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Address Delete
# =========================================================

address_delete_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_delete",
    summary="Delete User Address",
    description=(
        "Deletes an address belonging to the authenticated user. "
        "If the deleted address was the default address, "
        "another address will automatically become the default."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address deleted successfully.",
            examples=[
                OpenApiExample(
                    name="Address Deleted Successfully",
                    value=responses.AddressDeleteAPIViewSuccess,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address not found.",
            examples=[
                OpenApiExample(
                    name="Address Not Found",
                    value=responses.AddressNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Set Default Address
# =========================================================

address_set_default_view_schema = extend_schema(
    tags=["Addresses"],
    operation_id="address_set_default",
    summary="Set Default Address",
    description=(
        "Sets the selected address as the default address "
        "for the authenticated user. "
        "Any previously selected default address "
        "will automatically be unset."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Default address changed successfully.",
            examples=[
                OpenApiExample(
                    name="Default Address Changed",
                    value=responses.AddressSetDefaultAPIViewSuccess,
                    media_type="application/json",
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
                    value=responses.AddressAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Address not found.",
            examples=[
                OpenApiExample(
                    name="Address Not Found",
                    value=responses.AddressNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)
