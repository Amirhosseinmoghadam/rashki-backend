from payments.models import (
    PaymentAttempt,
)

from .base import (
    PaymentProviderConfigurationError,
)

from .tcart import (
    TCartProvider,
)

from .zarinpal import (
    ZarinPalProvider,
)


# =========================================================
# Provider Registry
# =========================================================


def get_payment_provider(
    provider,
):

    if (
        provider
        == PaymentAttempt
        .Provider
        .ZARINPAL
    ):

        return ZarinPalProvider()

    if (
        provider
        == PaymentAttempt
        .Provider
        .TCART
    ):

        return TCartProvider()

    raise PaymentProviderConfigurationError(
        "Provider پرداخت معتبر نیست."
    )