from shipping.models import (
    ShippingOrigin,
)


class ShippingOriginNotConfigured(
    Exception
):
    pass


def get_default_shipping_origin():
    """
    مبدا فعلی سایت برای Quoteهای جدید.

    تغییر این مقدار هیچ اثری روی Orderهای
    ثبت‌شده قبلی ندارد.
    """

    origin = (
        ShippingOrigin.objects
        .select_related(
            "province",
            "city",
        )
        .filter(
            is_active=True,
            is_default=True,
        )
        .first()
    )

    if origin is None:
        raise ShippingOriginNotConfigured(
            (
                "هیچ مبدا ارسال پیش‌فرض "
                "فعالی تعریف نشده است."
            )
        )

    return origin