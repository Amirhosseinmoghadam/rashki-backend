from .models import (
    ShippingMethod,
)


def get_active_shipping_methods():

    return (
        ShippingMethod.objects
        .filter(
            is_active=True
        )
        .order_by(
            "sort_order",
            "id",
        )
    )