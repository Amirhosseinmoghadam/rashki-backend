from django.urls import path

from .views import (
    CartListView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

app_name = "carts_api_v1"


urlpatterns = [
    # =====================================================
    # Cart Management
    # =====================================================
    path(
        "",
        CartListView.as_view(),
        name="cart-list",
    ),
    path(
        "add/",
        AddToCartView.as_view(),
        name="cart-add",
    ),
    path(
        "<int:item_id>/",
        UpdateCartItemView.as_view(),
        name="cart-item-update",
    ),
    path(
        "<int:item_id>/remove/",
        RemoveCartItemView.as_view(),
        name="cart-item-remove",
    ),
    path(
        "clear/",
        ClearCartView.as_view(),
        name="cart-clear",
    ),
]
