from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    SendOTPView,
    OTPVerifyView,
    CompleteProfileView,
    UserLogoutAPIView,

    #Address
    AddressDetailAPIView,
    AddressListCreateAPIView,
    AddressSetDefaultAPIView,
)

from accounts.api.v1.openapi.schema import DecoratedTokenRefreshView

app_name = "accounts_api_v1"


urlpatterns = [
    # =====================================================
    # Authentication
    # =====================================================
    path(
        "send-otp/",
        SendOTPView.as_view(),
        name="send-otp",
    ),
    path(
        "verify-otp/",
        OTPVerifyView.as_view(),
        name="verify-otp",
    ),
    # =====================================================
    # Profile
    # =====================================================
    path(
        "complete-profile/",
        CompleteProfileView.as_view(),
        name="complete-profile",
    ),
    # =====================================================
    # JWT
    # =====================================================
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "token/refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"
    ),
    # =====================================================
    # Logout
    # =====================================================
    path(
        "logout/",
        UserLogoutAPIView.as_view(),
        name="logout",
    ),
    # =====================================================
    # Address
    # =====================================================
    path(
        "addresses/",
        AddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),

    path(
        "addresses/<int:pk>/",
        AddressDetailAPIView.as_view(),
        name="address-detail",
    ),

    path(
        "addresses/<int:pk>/set-default/",
        AddressSetDefaultAPIView.as_view(),
        name="address-set-default",
    ),




]
