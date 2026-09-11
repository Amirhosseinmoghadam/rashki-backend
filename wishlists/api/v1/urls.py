from django.urls import path

from .views import (
    WishlistListAPIView,
    WishlistItemAPIView,
    WishlistProductIdsAPIView,
)


app_name = "wishlists_api_v1"


urlpatterns = [

    # لیست کامل Wishlist
    path(
        "wishlist/",
        WishlistListAPIView.as_view(),
        name="wishlist-list",
    ),

    # لیست سبک Product IDها
    path(
        "wishlist/product-ids/",
        WishlistProductIdsAPIView.as_view(),
        name="wishlist-product-ids",
    ),

    # افزودن یا حذف Product
    path(
        "wishlist/<int:product_id>/",
        WishlistItemAPIView.as_view(),
        name="wishlist-item",
    ),
]