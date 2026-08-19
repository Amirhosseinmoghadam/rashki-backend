from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema_view,
)

from . import examples, responses

from contact.api.v1.serializers import (
    ContactRequestCreateSerializer,
    ContactRequestAdminSerializer,
)


# =========================================================
# Contact Create
# =========================================================

contact_create_view_schema = extend_schema(
    tags=["Contact"],
    operation_id="contact_create",
    summary="Create Contact Request",
    description=(
        "Creates a new contact request. "
        "This endpoint is publicly accessible and "
        "does not require authentication. "
        "The request is protected by rate limiting "
        "to prevent abuse and spam."
    ),
    request=ContactRequestCreateSerializer,
    examples=[
        OpenApiExample(
            name="Price Inquiry",
            value=examples.ContactCreateAPIViewExample,
            media_type="application/json",
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Contact request created successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Contact Request Created Successfully",
                    value=responses.ContactCreateAPIViewSuccess,
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
                    name="Invalid First Name",
                    value=responses.ContactInvalidFirstName,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Last Name",
                    value=responses.ContactInvalidLastName,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Phone Number",
                    value=responses.ContactInvalidPhoneNumber,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Subject",
                    value=responses.ContactInvalidSubject,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Description",
                    value=responses.ContactInvalidDescription,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Duplicate Request",
                    value=responses.ContactDuplicateRequest,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Too many requests. "
                "The client has exceeded the allowed "
                "number of contact requests."
            ),
            examples=[
                OpenApiExample(
                    name="Rate Limit Exceeded",
                    value=responses.ContactRateLimitExceeded,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Contact Admin List
# =========================================================

contact_admin_list_view_schema = extend_schema(
    tags=["Contact"],
    operation_id="contact_admin_list",
    summary="List Contact Requests",
    description=(
        "Returns all contact requests. "
        "This endpoint is restricted to authenticated "
        "staff or admin users."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Contact requests retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Contact Requests Retrieved Successfully",
                    value=responses.ContactAdminListAPIViewSuccess,
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
                    value=responses.ContactAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Authenticated user does not have "
                "admin/staff permissions."
            ),
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=responses.ContactPermissionDenied,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Contact Admin Detail
# =========================================================

contact_admin_detail_view_schema = extend_schema(
    tags=["Contact"],
    operation_id="contact_admin_detail",
    summary="Get Contact Request",
    description=(
        "Returns a single contact request. "
        "Only authenticated staff or admin users "
        "can access this endpoint."
    ),
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Contact request retrieved successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Contact Request Retrieved Successfully",
                    value=responses.ContactAdminDetailAPIViewSuccess,
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
                    value=responses.ContactAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Permission denied.",
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=responses.ContactPermissionDenied,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Contact request not found.",
            examples=[
                OpenApiExample(
                    name="Contact Request Not Found",
                    value=responses.ContactNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Contact Admin Partial Update
# =========================================================

contact_admin_partial_update_view_schema = extend_schema(
    tags=["Contact"],
    operation_id="contact_admin_partial_update",
    summary="Update Contact Request Status",
    description=(
        "Partially updates a contact request. "
        "Only the is_read field can be modified by the admin. "
        "Customer information and request content are read-only."
    ),
    request=ContactRequestAdminSerializer,
    examples=[
        OpenApiExample(
            name="Mark As Read",
            value=examples.ContactAdminPartialUpdateAPIViewExample,
            media_type="application/json",
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Contact request updated successfully."
            ),
            examples=[
                OpenApiExample(
                    name="Contact Request Updated Successfully",
                    value=(
                        responses.ContactAdminPartialUpdateAPIViewSuccess
                    ),
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Validation error.",
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Authentication required.",
            examples=[
                OpenApiExample(
                    name="Authentication Required",
                    value=responses.ContactAuthenticationRequired,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Permission denied.",
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=responses.ContactPermissionDenied,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        404: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Contact request not found.",
            examples=[
                OpenApiExample(
                    name="Contact Request Not Found",
                    value=responses.ContactNotFound,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)