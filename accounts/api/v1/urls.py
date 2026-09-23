from django.urls import path

from .views import (
    AccountTokenRefreshView,
    CompleteProfileView,
    OTPVerifyView,
    SendOTPView,
    UserLogoutAPIView,
    UserMeAPIView,
)


app_name = "accounts_api_v1"


urlpatterns = [
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
    path(
        "complete-profile/",
        CompleteProfileView.as_view(),
        name="complete-profile",
    ),
    path(
        "me/",
        UserMeAPIView.as_view(),
        name="me",
    ),
    path(
        "token/refresh/",
        AccountTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        UserLogoutAPIView.as_view(),
        name="logout",
    ),
]
