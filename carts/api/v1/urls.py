from django.urls import path

from .views import (
    CartAPIView,
    CartClearAPIView,
    CartDiscountAPIView,
    CartItemAPIView,
    CartItemAddAPIView,
)


app_name = "carts_api_v1"


urlpatterns = [

    # دریافت Cart
    path(
        "cart/",
        CartAPIView.as_view(),
        name="cart-detail",
    ),

    # افزودن Product
    path(
        "cart/items/",
        CartItemAddAPIView.as_view(),
        name="cart-item-add",
    ),

    # تغییر Quantity / حذف Product
    path(
        "cart/items/<int:product_id>/",
        CartItemAPIView.as_view(),
        name="cart-item",
    ),

    # خالی کردن Cart
    path(
        "cart/clear/",
        CartClearAPIView.as_view(),
        name="cart-clear",
    ),

    # اعمال / حذف Discount Code
    path(
        "cart/discount/",
        CartDiscountAPIView.as_view(),
        name="cart-discount",
    ),
]