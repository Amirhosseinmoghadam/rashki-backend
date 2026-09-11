from shipping.models import (
    ShippingMethod,
)

from .manual import (
    ManualTariffProvider,
)

from .post_pishtaz import (
    PostPishtazProvider,
)

from .tipax import (
    TipaxProvider,
)

from .base import (
    ShippingProviderUnavailableError,
)


def get_shipping_provider(
    method,
):

    # =====================================================
    # Manual
    # =====================================================

    if (
        method.calculation_mode
        == ShippingMethod
        .CalculationMode
        .MANUAL
    ):

        return ManualTariffProvider()

    # =====================================================
    # API
    # =====================================================

    if (
        method.provider
        == ShippingMethod.Provider.POST
    ):

        return PostPishtazProvider()

    if (
        method.provider
        == ShippingMethod.Provider.TIPAX
    ):

        return TipaxProvider()

    raise ShippingProviderUnavailableError(
        "Provider این روش ارسال "
        "پیکربندی نشده است."
    )