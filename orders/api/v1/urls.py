from django.urls import path

from .views import (
    OrderCancelAPIView,
    OrderDetailAPIView,
    OrderListCreateAPIView,
)


app_name = "orders_api_v1"


urlpatterns = [

    # =====================================================
    # List / Checkout
    # =====================================================

    path(
        "orders/",
        OrderListCreateAPIView.as_view(),
        name="order-list-create",
    ),

    # =====================================================
    # Cancel
    # =====================================================

    path(
        "orders/<str:order_number>/cancel/",
        OrderCancelAPIView.as_view(),
        name="order-cancel",
    ),

    # =====================================================
    # Detail
    # =====================================================

    path(
        "orders/<str:order_number>/",
        OrderDetailAPIView.as_view(),
        name="order-detail",
    ),
]