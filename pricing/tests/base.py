from decimal import Decimal
from types import SimpleNamespace
from pricing.models import PricingSettings
from products.models import Product


def product_stub(mode=Product.PricingMode.FIXED, **kwargs):
    data = dict(pricing_mode=mode, base_price_toman=100000, base_price_usd=None,
                markup_percent=Decimal("0"), fixed_cost_toman=0,
                is_price_locked=False, pk=77, current_price_toman=None,
                last_exchange_rate_toman=None, price_updated_at=None)
    data.update(kwargs)
    return SimpleNamespace(**data)


def settings_stub(step=1000, mode=PricingSettings.RoundingMode.NEAREST):
    return SimpleNamespace(rounding_step_toman=step, rounding_mode=mode)
