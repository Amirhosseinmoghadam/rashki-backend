from rest_framework import serializers

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

from contact.api.v1.serializers import (
    ContactRequestCreateSerializer,
    ContactRequestAdminSerializer,
    ContactRequestStatusSerializer,
)

from . import (
    examples,
    responses,
)


# =========================================================
# Reusable Response Schemas
# =========================================================


ContactCreateDataSerializer = inline_serializer(
    name="ContactCreateData",
    fields={
        "id": serializers.IntegerField(),
    },
)


ContactCreateResponseSerializer = inline_serializer(
    name="ContactCreateResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ContactCreateDataSerializer,
    },
)


# =========================================================
# Admin Pagination
# =========================================================


ContactAdminPaginatedDataSerializer = (
    inline_serializer(
        name="ContactAdminPaginatedData",
        fields={
            "count": (
                serializers.IntegerField()
            ),
            "next": serializers.CharField(
                allow_null=True,
            ),
            "previous": serializers.CharField(
                allow_null=True,
            ),
            "results": (
                ContactRequestAdminSerializer(
                    many=True
                )
            ),
        },
    )
)


ContactAdminListResponseSerializer = (
    inline_serializer(
        name="ContactAdminListResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                ContactAdminPaginatedDataSerializer
            ),
        },
    )
)


# =========================================================
# Admin Detail Response
# =========================================================


ContactAdminDetailResponseSerializer = (
    inline_serializer(
        name="ContactAdminDetailResponse",
        fields={
            "success": (
                serializers.BooleanField()
            ),
            "message": (
                serializers.CharField()
            ),
            "data": (
                ContactRequestAdminSerializer()
            ),
        },
    )
)


# =========================================================
# Contact Create
# =========================================================


contact_create_view_schema = extend_schema(
    tags=[
        "Contact",
    ],
    operation_id="contact_create",
    summary="Create Contact Request",
    description=(
        "Creates a new contact request. "
        "This endpoint is publicly accessible "
        "and does not require authentication. "
        "Rate limiting and duplicate-request "
        "protection are applied."
    ),
    request=ContactRequestCreateSerializer,
    examples=[
        OpenApiExample(
            name="Price Inquiry",
            value=(
                examples
                .ContactCreateAPIViewExample
            ),
            media_type="application/json",
            request_only=True,
        ),
    ],
    responses={
        201: OpenApiResponse(
            response=(
                ContactCreateResponseSerializer
            ),
            description=(
                "Contact request created "
                "successfully."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Contact Request Created"
                    ),
                    value=(
                        responses
                        .ContactCreateAPIViewSuccess
                    ),
                    media_type=(
                        "application/json"
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
                    name="Invalid First Name",
                    value=(
                        responses
                        .ContactInvalidFirstName
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Last Name",
                    value=(
                        responses
                        .ContactInvalidLastName
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Phone Number",
                    value=(
                        responses
                        .ContactInvalidPhoneNumber
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Subject",
                    value=(
                        responses
                        .ContactInvalidSubject
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid Description",
                    value=(
                        responses
                        .ContactInvalidDescription
                    ),
                    response_only=True,
                ),
                OpenApiExample(
                    name="Duplicate Request",
                    value=(
                        responses
                        .ContactDuplicateRequest
                    ),
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Contact request rate limit "
                "exceeded."
            ),
            examples=[
                OpenApiExample(
                    name="Rate Limit Exceeded",
                    value=(
                        responses
                        .ContactRateLimitExceeded
                    ),
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
    tags=[
        "Contact",
    ],
    operation_id="contact_admin_list",
    summary="List Contact Requests",
    description=(
        "Returns paginated contact requests. "
        "Only staff/admin users can access "
        "this endpoint."
    ),
    responses={
        200: OpenApiResponse(
            response=(
                ContactAdminListResponseSerializer
            ),
            description=(
                "Contact requests retrieved "
                "successfully."
            ),
            examples=[
                OpenApiExample(
                    name=(
                        "Contact Requests Retrieved"
                    ),
                    value=(
                        responses
                        .ContactAdminListAPIViewSuccess
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
                        .ContactAuthenticationRequired
                    ),
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "Admin/staff permission required."
            ),
            examples=[
                OpenApiExample(
                    name="Permission Denied",
                    value=(
                        responses
                        .ContactPermissionDenied
                    ),
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Contact Admin Detail
# =========================================================


contact_admin_detail_view_schema = (
    extend_schema(
        tags=[
            "Contact",
        ],
        operation_id=(
            "contact_admin_detail"
        ),
        summary="Get Contact Request",
        description=(
            "Returns a single contact request. "
            "Only staff/admin users can access "
            "this endpoint."
        ),
        responses={
            200: OpenApiResponse(
                response=(
                    ContactAdminDetailResponseSerializer
                ),
                description=(
                    "Contact request retrieved "
                    "successfully."
                ),
                examples=[
                    OpenApiExample(
                        name=(
                            "Contact Request "
                            "Retrieved"
                        ),
                        value=(
                            responses
                            .ContactAdminDetailAPIViewSuccess
                        ),
                        response_only=True,
                    ),
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
                            .ContactAuthenticationRequired
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
                            .ContactPermissionDenied
                        ),
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description=(
                    "Contact request not found."
                ),
                examples=[
                    OpenApiExample(
                        name=(
                            "Contact Request "
                            "Not Found"
                        ),
                        value=(
                            responses
                            .ContactNotFound
                        ),
                        response_only=True,
                    ),
                ],
            ),
        },
    )
)


# =========================================================
# Contact Admin Partial Update
# =========================================================


contact_admin_partial_update_view_schema = (
    extend_schema(
        tags=[
            "Contact",
        ],
        operation_id=(
            "contact_admin_partial_update"
        ),
        summary=(
            "Update Contact Request Status"
        ),
        description=(
            "Updates the read status of a "
            "contact request. "
            "Only the is_read field can be "
            "modified."
        ),
        request=(
            ContactRequestStatusSerializer
        ),
        examples=[
            OpenApiExample(
                name="Mark As Read",
                value=(
                    examples
                    .ContactAdminPartialUpdateAPIViewExample
                ),
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=(
                    ContactAdminDetailResponseSerializer
                ),
                description=(
                    "Contact request status "
                    "updated successfully."
                ),
                examples=[
                    OpenApiExample(
                        name=(
                            "Contact Request Updated"
                        ),
                        value=(
                            responses
                            .ContactAdminPartialUpdateAPIViewSuccess
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
                        name=(
                            "Invalid Read Status"
                        ),
                        value=(
                            responses
                            .ContactInvalidReadStatus
                        ),
                        response_only=True,
                    ),
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
                            .ContactAuthenticationRequired
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
                            .ContactPermissionDenied
                        ),
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description=(
                    "Contact request not found."
                ),
                examples=[
                    OpenApiExample(
                        name=(
                            "Contact Request "
                            "Not Found"
                        ),
                        value=(
                            responses
                            .ContactNotFound
                        ),
                        response_only=True,
                    ),
                ],
            ),
        },
    )
)