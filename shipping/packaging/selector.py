from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from itertools import permutations

from shipping.models import (
    ShippingMethod,
    ShippingProviderPackingOption,
)


# =========================================================
# Exceptions
# =========================================================


class PackagingSelectionError(
    Exception
):
    pass


# =========================================================
# Result
# =========================================================


@dataclass(frozen=True)
class PackingSelection:

    packing: (
        ShippingProviderPackingOption
    )

    product_dimensions: tuple[
        Decimal,
        Decimal,
        Decimal,
    ]

    fitted_orientation: tuple[
        Decimal,
        Decimal,
        Decimal,
    ]

    weight_grams: int

    @property
    def provider_packing_id(
        self,
    ):
        return (
            self.packing
            .provider_packing_id
        )


# =========================================================
# Decimal
# =========================================================


def _decimal(
    value,
    *,
    field_name,
):
    try:

        result = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:

        raise PackagingSelectionError(
            (
                f"{field_name} "
                "برای محاسبه بسته‌بندی معتبر نیست."
            )
        ) from exc

    if result <= 0:

        raise PackagingSelectionError(
            (
                f"{field_name} "
                "باید بیشتر از صفر باشد."
            )
        )

    return result


# =========================================================
# Orientations
# =========================================================


def _orientations(
    length,
    width,
    height,
):
    """
    محصول می‌تواند داخل کارتن چرخانده شود.

    مثلاً:
        20 × 10 × 15

    می‌تواند به صورت:
        15 × 20 × 10
        10 × 15 × 20
        ...

    قرار بگیرد.
    """

    values = (
        length,
        width,
        height,
    )

    return sorted(
        set(
            permutations(
                values,
                3,
            )
        )
    )


# =========================================================
# Fit
# =========================================================


def _find_fitting_orientation(
    *,
    item_length,
    item_width,
    item_height,
    box_length,
    box_width,
    box_height,
):
    for orientation in _orientations(
        item_length,
        item_width,
        item_height,
    ):

        length, width, height = (
            orientation
        )

        if (
            length <= box_length
            and width <= box_width
            and height <= box_height
        ):
            return orientation

    return None


# =========================================================
# Select Tipax Carton
# =========================================================


def select_tipax_carton_for_product(
    *,
    product,
    quantity=1,
    dimension_margin_cm=Decimal("1.00"),
    extra_weight_grams=150,
):
    """
    انتخاب کوچک‌ترین کارتن مناسب Tipax
    برای یک واحد/محصول.

    معیارها:

        - ابعاد محصول
        - امکان چرخاندن محصول
        - وزن
        - حاشیه امن ابعادی
        - کوچک‌ترین حجم کارتن

    فعلاً quantity فقط برای وزن کل استفاده نمی‌شود.
    بسته‌بندی چند محصول در مرحله Cart Packaging
    توسط Strategy جدا انجام می‌شود.
    """

    if quantity != 1:

        raise PackagingSelectionError(
            (
                "این Selector مخصوص یک واحد محصول است. "
                "برای چند محصول از Cart Packaging Strategy استفاده شود."
            )
        )

    if not getattr(
        product,
        "weight_grams",
        None,
    ):
        raise PackagingSelectionError(
            (
                f"وزن محصول «{product}» "
                "تعریف نشده است."
            )
        )

    raw_length = getattr(
        product,
        "shipping_length_cm",
        None,
    )

    raw_width = getattr(
        product,
        "shipping_width_cm",
        None,
    )

    raw_height = getattr(
        product,
        "shipping_height_cm",
        None,
    )

    if (
        raw_length is None
        or raw_width is None
        or raw_height is None
    ):
        raise PackagingSelectionError(
            (
                f"ابعاد ارسال محصول «{product}» "
                "کامل تعریف نشده است."
            )
        )

    length = _decimal(
        raw_length,
        field_name="طول",
    )

    width = _decimal(
        raw_width,
        field_name="عرض",
    )

    height = _decimal(
        raw_height,
        field_name="ارتفاع",
    )

    margin = Decimal(
        str(
            dimension_margin_cm
        )
    )

    required_length = (
        length + margin
    )

    required_width = (
        width + margin
    )

    required_height = (
        height + margin
    )

    try:

        total_weight_grams = (
            int(
                product.weight_grams
            )
            +
            int(
                extra_weight_grams
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise PackagingSelectionError(
            "وزن محصول معتبر نیست."
        ) from exc

    weight_kg = (
        Decimal(
            total_weight_grams
        )
        /
        Decimal("1000")
    )

    candidates = []

    cartons = (
        ShippingProviderPackingOption
        .objects
        .filter(
            provider=(
                ShippingMethod
                .Provider
                .TIPAX
            ),
            kind=(
                ShippingProviderPackingOption
                .Kind
                .CARTON
            ),
            pack_type=20,
            is_active=True,
        )
        .exclude(
            length__isnull=True
        )
        .exclude(
            width__isnull=True
        )
        .exclude(
            height__isnull=True
        )
    )

    for carton in cartons:

        # -------------------------
        # Max provider weight
        # -------------------------

        if (
            carton.max_weight
            is not None
            and weight_kg
            > carton.max_weight
        ):
            continue

        orientation = (
            _find_fitting_orientation(
                item_length=(
                    required_length
                ),
                item_width=(
                    required_width
                ),
                item_height=(
                    required_height
                ),
                box_length=(
                    carton.length
                ),
                box_width=(
                    carton.width
                ),
                box_height=(
                    carton.height
                ),
            )
        )

        if orientation is None:
            continue

        volume = carton.volume

        if volume is None:
            continue

        candidates.append(
            (
                volume,
                carton.box_number
                or 9999,
                carton.pk,
                carton,
                orientation,
            )
        )

    if not candidates:

        raise PackagingSelectionError(
            (
                "هیچ کارتن مناسب Tipax برای "
                f"محصول «{product}» پیدا نشد."
            )
        )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        )
    )

    (
        _volume,
        _box_number,
        _pk,
        carton,
        orientation,
    ) = candidates[0]

    return PackingSelection(
        packing=carton,
        product_dimensions=(
            length,
            width,
            height,
        ),
        fitted_orientation=(
            orientation
        ),
        weight_grams=(
            total_weight_grams
        ),
    )