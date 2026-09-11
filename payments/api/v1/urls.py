from django.urls import path

from .views import (
    PaymentDetailAPIView,
    PaymentRefundCreateAPIView,
    PaymentRefundDetailAPIView,
    PaymentRefundExecuteAPIView,
    PaymentStartAPIView,
    TCartCallbackAPIView,
    ZarinPalCallbackAPIView,
)


app_name = "payments_api_v1"


urlpatterns = [

    # =====================================================
    # Payment
    # =====================================================

    # شروع پرداخت
    path(
        "payments/start/",
        PaymentStartAPIView.as_view(),
        name="payment-start",
    ),

    # وضعیت Attempt
    path(
        "payments/<uuid:public_id>/",
        PaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),

    # Callback زرین‌پال
    path(
        (
            "payments/zarinpal/"
            "callback/<uuid:public_id>/"
        ),
        ZarinPalCallbackAPIView.as_view(),
        name="zarinpal-callback",
    ),

    # Webhook TCart
    path(
        (
            "payments/tcart/"
            "callback/<uuid:public_id>/"
        ),
        TCartCallbackAPIView.as_view(),
        name="tcart-callback",
    ),


    # =====================================================
    # Refund
    # =====================================================

    # ایجاد Refund
    path(
        "payments/refunds/",
        PaymentRefundCreateAPIView.as_view(),
        name="refund-create",
    ),

    # جزئیات Refund
    path(
        "payments/refunds/<uuid:public_id>/",
        PaymentRefundDetailAPIView.as_view(),
        name="refund-detail",
    ),

    # اجرای واقعی Refund
    path(
        (
            "payments/refunds/"
            "<uuid:public_id>/execute/"
        ),
        PaymentRefundExecuteAPIView.as_view(),
        name="refund-execute",
    ),
]