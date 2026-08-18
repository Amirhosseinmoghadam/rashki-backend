from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema_view,
)
from rest_framework_simplejwt.views import TokenRefreshView

from . import examples, responses

from accounts.api.v1.serializers import (
    SendOTPSerializer,
    OTPVerifySerializer,
    CompleteProfileSerializer,
    AddressSerializer,
    AddressCreateSerializer,
    AddressUpdateSerializer,
)




# Define the decorated view object here
DecoratedTokenRefreshView = extend_schema_view(
    post=extend_schema(
        summary="Refresh JWT Access Token",
        description="Use a valid refresh token to obtain a new access token.",
        tags=["Authentication (Accounts Login)"],
    )
)(TokenRefreshView)

# =========================================================
# Send OTP
# =========================================================

send_otp_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="send_otp",
    summary="Send Authentication OTP",
    description=(
        "Sends an authentication OTP to the provided phone number. "
        "This endpoint is used for both existing and new users. "
        "A previously active OTP is invalidated before creating a new one. "
        "The OTP itself is never returned in the response."
    ),
    request=SendOTPSerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.SendOTPViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="OTP sent successfully.",
            examples=[
                OpenApiExample(
                    name="OTP Sent Successfully",
                    value=responses.SendOTPViewOTPSentSuccessfully,
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
                    value={
                        "phone_number": [
                            "شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد."
                        ]
                    },
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Too many OTP requests.",
            examples=[
                OpenApiExample(
                    name="Rate Limit Exceeded",
                    value=responses.SendOTPViewRateLimitExceeded,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# OTP Verify
# =========================================================

otp_verify_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="verify_otp",
    summary="Verify Authentication OTP",
    description=(
        "Verifies the OTP sent to the user's phone number. "
        "For an existing user, this completes authentication. "
        "For a new user, the user is created automatically after "
        "successful OTP verification. "
        "The response contains JWT access and refresh tokens "
        "and indicates whether the user needs to complete their profile."
    ),
    request=OTPVerifySerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.OTPVerifyViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="OTP verified successfully and JWT tokens generated.",
            examples=[
                OpenApiExample(
                    name="Existing User - Profile Completed",
                    value=responses.OTPVerifyViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="New User - Profile Incomplete",
                    value=responses.OTPVerifyViewSuccessNewUser,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=("Invalid, expired, or otherwise unusable OTP."),
            examples=[
                OpenApiExample(
                    name="Invalid OTP",
                    value=responses.OTPVerifyViewInvalidOTP,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Expired OTP",
                    value=responses.OTPVerifyViewExpiredOTP,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Invalid OTP Code",
                    value=responses.OTPVerifyViewInvalidCode,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        429: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=(
                "OTP verification rate limit exceeded "
                "or maximum OTP attempts reached."
            ),
            examples=[
                OpenApiExample(
                    name="Verification Rate Limit",
                    value=responses.OTPVerifyViewRateLimitExceeded,
                    media_type="application/json",
                    response_only=True,
                ),
                OpenApiExample(
                    name="Maximum Attempts Exceeded",
                    value=responses.OTPVerifyViewMaxAttemptsExceeded,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
)


# =========================================================
# Complete Profile
# =========================================================

complete_profile_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="complete_profile",
    summary="Complete User Profile",
    description=(
        "Updates the authenticated user's basic profile information. "
        "The phone number cannot be changed through this endpoint. "
        "After successful completion, the user can continue to the home page."
    ),
    request=CompleteProfileSerializer,
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.CompleteProfileViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="User profile updated successfully.",
            examples=[
                OpenApiExample(
                    name="Profile Completed",
                    value=responses.CompleteProfileViewSuccess,
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
                    value={"first_name": ["این فیلد الزامی است."]},
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
# Logout
# =========================================================

user_logout_api_view_schema = extend_schema(
    tags=["Authentication"],
    operation_id="logout",
    summary="Logout User",
    description=(
        "Logs out the authenticated user by blacklisting " "the provided refresh token."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "string",
                    "description": "JWT refresh token.",
                },
            },
            "required": ["refresh"],
        }
    },
    examples=[
        OpenApiExample(
            name="Example Request",
            value=examples.UserLogoutAPIViewExample,
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="User logged out successfully.",
            examples=[
                OpenApiExample(
                    name="Logout Successful",
                    value=responses.UserLogoutAPIViewSuccess,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        400: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Refresh token was not provided.",
            examples=[
                OpenApiExample(
                    name="Missing Refresh Token",
                    value=responses.UserLogoutAPIViewMissingRefreshToken,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description=("Refresh token is invalid or has already been blacklisted."),
            examples=[
                OpenApiExample(
                    name="Invalid Refresh Token",
                    value=responses.UserLogoutAPIViewInvalidRefreshToken,
                    media_type="application/json",
                    response_only=True,
                ),
            ],
        ),
    },
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
