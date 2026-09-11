from .base import (
    BaseShippingProvider,
    ShippingProviderUnavailableError,
)


class PostPishtazProvider(
    BaseShippingProvider
):

    def quote(
        self,
        *,
        method,
        destination_address,
        weight_grams,
    ):

        # وقتی مستندات رسمی/API Access
        # پست را دریافت کردیم اینجا پیاده‌سازی می‌شود.
        raise ShippingProviderUnavailableError(
            "اتصال API پست پیشتاز "
            "هنوز پیکربندی نشده است."
        )