from django.db.models import Prefetch

from .models import (
    Order,
    OrderItem,
)


# =========================================================
# Order QuerySet
# =========================================================


def get_order_queryset():

    order_items = (
        OrderItem.objects
        .select_related(
            "product",
        )
        .order_by(
            "id"
        )
    )

    return (
        Order.objects
        .select_related(
            "user",
            "address",
            "shipping_method",
            "discount",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=order_items,
            )
        )
    )


# =========================================================
# User Orders
# =========================================================


def get_user_orders(
    user,
):

    return (
        get_order_queryset()
        .filter(
            user=user
        )
        .order_by(
            "-created_at"
        )
    )