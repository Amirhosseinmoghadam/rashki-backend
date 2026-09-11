from decimal import (
    Decimal,
    ROUND_CEILING,
)

from django.db.models import Q
from django.utils import timezone

from shipping.models import (
    ShippingRateRule,
)

from .base import (
    BaseShippingProvider,
    ProviderQuote,
    ShippingRateNotFoundError,
)


class ManualTariffProvider(
    BaseShippingProvider
):

    # =====================================================
    # Rule Lookup
    # =====================================================

    def _get_rule(
        self,
        *,
        method,
        destination_address,
        weight_grams,
    ):

        now = timezone.now()

        base_queryset = (
            ShippingRateRule.objects
            .filter(
                method=method,
                is_active=True,
                effective_from__lte=now,
                min_weight_grams__lte=(
                    weight_grams
                ),
            )
            .filter(
                Q(
                    effective_to__isnull=True
                )
                |
                Q(
                    effective_to__gt=now
                )
            )
            .filter(
                Q(
                    max_weight_grams__isnull=True
                )
                |
                Q(
                    max_weight_grams__gte=(
                        weight_grams
                    )
                )
            )
            .select_related(
                "province",
                "city",
            )
        )

        # ---------------------------------------------
        # City Rule
        # ---------------------------------------------

        rule = (
            base_queryset
            .filter(
                destination_scope=(
                    ShippingRateRule
                    .DestinationScope
                    .CITY
                ),
                city_id=(
                    destination_address
                    .city_id
                ),
            )
            .order_by(
                "-priority",
                "-effective_from",
                "-id",
            )
            .first()
        )

        if rule:
            return rule

        # ---------------------------------------------
        # Province Rule
        # ---------------------------------------------

        rule = (
            base_queryset
            .filter(
                destination_scope=(
                    ShippingRateRule
                    .DestinationScope
                    .PROVINCE
                ),
                province_id=(
                    destination_address
                    .province_id
                ),
            )
            .order_by(
                "-priority",
                "-effective_from",
                "-id",
            )
            .first()
        )

        if rule:
            return rule

        # ---------------------------------------------
        # Nationwide Rule
        # ---------------------------------------------

        rule = (
            base_queryset
            .filter(
                destination_scope=(
                    ShippingRateRule
                    .DestinationScope
                    .NATIONWIDE
                ),
            )
            .order_by(
                "-priority",
                "-effective_from",
                "-id",
            )
            .first()
        )

        if rule:
            return rule

        raise ShippingRateNotFoundError(
            "برای این روش ارسال، مقصد و وزن "
            "تعرفه‌ای تعریف نشده است."
        )

    # =====================================================
    # Quote
    # =====================================================

    def quote(
        self,
        *,
        method,
        destination_address,
        weight_grams,
    ):

        rule = self._get_rule(
            method=method,
            destination_address=(
                destination_address
            ),
            weight_grams=weight_grams,
        )

        extra_grams = max(
            0,
            weight_grams
            - rule.included_weight_grams,
        )

        # هر بخش از یک کیلوگرم اضافه
        # یک کیلو کامل حساب می‌شود.
        extra_kilos = int(
            (
                Decimal(extra_grams)
                / Decimal("1000")
            ).quantize(
                Decimal("1"),
                rounding=ROUND_CEILING,
            )
        )

        amount = (
            rule.base_price_toman
            +
            (
                extra_kilos
                * rule.additional_per_kg_toman
            )
        )

        return ProviderQuote(
            amount_toman=amount,
            provider_data={
                "calculation": "manual",
                "rule_id": rule.id,
                "extra_kilos": extra_kilos,
            },
        )