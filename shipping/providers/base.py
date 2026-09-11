from abc import (
    ABC,
    abstractmethod,
)

from dataclasses import dataclass


# =========================================================
# Exceptions
# =========================================================


class ShippingProviderError(Exception):
    """
    خطای پایه برای تمام Shipping Providerها.
    """

    pass


class ShippingProviderUnavailableError(
    ShippingProviderError
):
    """
    زمانی که Provider یا سرویس خارجی
    در حال حاضر در دسترس نیست.
    """

    pass


class ShippingRateNotFoundError(
    ShippingProviderError
):
    """
    زمانی که Provider نتواند تعرفه مناسب
    برای مقصد / وزن / سرویس پیدا کند.
    """

    pass


class ShippingProviderConfigurationError(
    ShippingProviderError
):
    """
    زمانی که تنظیمات Provider ناقص یا نامعتبر باشد.

    مثال:
    - Token تعریف نشده
    - Origin تعریف نشده
    - Credential ناقص است
    """

    pass


# =========================================================
# Provider Quote
# =========================================================


@dataclass
class ProviderQuote:
    """
    نتیجه استاندارد Quote بین تمام Providerها.

    amount_toman:
        مبلغ نهایی ارسال به تومان.

    provider_data:
        اطلاعات تکمیلی Provider برای Audit
        و Snapshot داخل Order.
    """

    amount_toman: int

    provider_data: dict | None = None


# =========================================================
# Base Shipping Provider
# =========================================================


class BaseShippingProvider(
    ABC
):
    """
    Interface مشترک تمام Shipping Providerها.
    """

    @abstractmethod
    @abstractmethod
    def quote(
            self,
            *,
            method,
            destination_address,
            weight_grams=None,
            package_value_toman=0,
            packages=None,
            origin=None,
    ) -> ProviderQuote:
        raise NotImplementedError