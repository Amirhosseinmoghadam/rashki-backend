from django.urls import path

from .views import (
    SendOTPAPIView,
    SendSimpleAPIView,
    SendAdvancedAPIView,
    SendSharedAPIView,
    SendMultipleAPIView,
    SendScheduleAPIView,
    DeliveryStatusAPIView,
    MessagesAPIView,
    InboxCountAPIView,
    CreditAPIView,
    PriceAPIView,

)


urlpatterns = [

    # Sending
    path(
        "send/otp/",
        SendOTPAPIView.as_view(),
        name="sms-send-otp",
    ),

    path(
        "send/simple/",
        SendSimpleAPIView.as_view(),
        name="sms-send-simple",
    ),

    path(
        "send/advanced/",
        SendAdvancedAPIView.as_view(),
        name="sms-send-advanced",
    ),

    path(
        "send/shared/",
        SendSharedAPIView.as_view(),
        name="sms-send-shared",
    ),

    path(
        "send/multiple/",
        SendMultipleAPIView.as_view(),
        name="sms-send-multiple",
    ),

    path(
        "send/schedule/",
        SendScheduleAPIView.as_view(),
        name="sms-send-schedule",
    ),

    # Status
    path(
        "status/",
        DeliveryStatusAPIView.as_view(),
        name="sms-status",
    ),

    # Receive
    path(
        "messages/",
        MessagesAPIView.as_view(),
        name="sms-messages",
    ),

    path(
        "inbox-count/",
        InboxCountAPIView.as_view(),
        name="sms-inbox-count",
    ),

    # Account
    path(
        "credit/",
        CreditAPIView.as_view(),
        name="sms-credit",
    ),

    path(
        "price/",
        PriceAPIView.as_view(),
        name="sms-price",
    ),


]