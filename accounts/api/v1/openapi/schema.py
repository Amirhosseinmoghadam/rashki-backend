from rest_framework import serializers

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from accounts.api.v1.serializers import (
    CompleteProfileSerializer,
    LogoutSerializer,
    OTPVerifySerializer,
    SendOTPSerializer,
    UserSerializer,
)

from . import examples, responses


GenericErrorResponse = inline_serializer(
    name="AccountsGenericErrorResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "errors": serializers.JSONField(
            allow_null=True,
        ),
    },
)

SendOTPSuccessResponse = inline_serializer(
    name="SendOTPSuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(),
    },
)

OTPVerifySuccessResponse = inline_serializer(
    name="OTPVerifySuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(),
    },
)

UserSuccessResponse = inline_serializer(
    name="AccountUserSuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": UserSerializer(),
    },
)

GenericSuccessResponse = inline_serializer(
    name="AccountsGenericSuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": serializers.JSONField(
            allow_null=True,
        ),
    },
)


send_otp_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="send_otp",
    summary="Send Authentication OTP",
    description=(
        "Sends a one-time authentication code. "
        "The endpoint is shared by login and signup."
    ),
    request=SendOTPSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.SendOTPRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=SendOTPSuccessResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.SendOTPSuccess,
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=GenericErrorResponse,
            examples=[
                OpenApiExample(
                    name="Validation Error",
                    value=responses.ValidationError,
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=GenericErrorResponse,
            examples=[
                OpenApiExample(
                    name="Rate Limited",
                    value=responses.RateLimitError,
                    response_only=True,
                ),
            ],
        ),
        503: OpenApiResponse(
            response=GenericErrorResponse,
            description="OTP delivery provider unavailable.",
        ),
    },
)


otp_verify_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="verify_otp",
    summary="Verify Authentication OTP",
    request=OTPVerifySerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.OTPVerifyRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OTPVerifySuccessResponse,
            examples=[
                OpenApiExample(
                    name="Existing User",
                    value=responses.OTPVerifyExistingUserSuccess,
                    response_only=True,
                ),
                OpenApiExample(
                    name="New User",
                    value=responses.OTPVerifyNewUserSuccess,
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=GenericErrorResponse,
            examples=[
                OpenApiExample(
                    name="Invalid OTP",
                    value=responses.InvalidOTPError,
                    response_only=True,
                ),
            ],
        ),
        403: OpenApiResponse(
            response=GenericErrorResponse,
            examples=[
                OpenApiExample(
                    name="Inactive User",
                    value=responses.InactiveUserError,
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=GenericErrorResponse,
        ),
    },
)


complete_profile_view_schema = extend_schema(
    tags=["Accounts"],
    operation_id="complete_profile",
    summary="Complete User Profile",
    request=CompleteProfileSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.CompleteProfileRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=GenericSuccessResponse,
        ),
        400: OpenApiResponse(
            response=GenericErrorResponse,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


me_get_view_schema = extend_schema(
    tags=["Accounts"],
    operation_id="account_me",
    summary="Get Current User",
    request=None,
    responses={
        200: OpenApiResponse(
            response=UserSuccessResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.ProfileSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


me_update_view_schema = extend_schema(
    tags=["Accounts"],
    operation_id="account_me_update",
    summary="Update Current User",
    request=CompleteProfileSerializer,
    responses={
        200: OpenApiResponse(
            response=UserSuccessResponse,
        ),
        400: OpenApiResponse(
            response=GenericErrorResponse,
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
        ),
    },
)


token_refresh_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="token_refresh",
    summary="Refresh JWT Access Token",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "string",
                },
            },
            "required": ["refresh"],
        }
    },
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.TokenRefreshRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=GenericSuccessResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.TokenRefreshSuccess,
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=GenericErrorResponse,
        ),
    },
)


user_logout_api_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="logout",
    summary="Logout User",
    request=LogoutSerializer,
    examples=[
        OpenApiExample(
            name="Request",
            value=examples.LogoutRequestExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=GenericSuccessResponse,
            examples=[
                OpenApiExample(
                    name="Success",
                    value=responses.LogoutSuccess,
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=GenericErrorResponse,
        ),
        401: OpenApiResponse(
            response=GenericErrorResponse,
        ),
        403: OpenApiResponse(
            response=GenericErrorResponse,
        ),
    },
)
