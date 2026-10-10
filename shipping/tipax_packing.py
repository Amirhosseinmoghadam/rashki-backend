from __future__ import annotations

import re
from decimal import (
    Decimal,
    InvalidOperation,
)

from django.db import transaction

from shipping.models import (
    ShippingMethod,
    ShippingProviderPackingOption,
)
from shipping.providers.tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


PROVIDER = ShippingMethod.Provider.TIPAX


class TipaxPackingSyncError(Exception):
    pass


# =========================================================
# Generic helpers
# =========================================================


def _extract_items(
    payload,
    *,
    label,
):
    if isinstance(
        payload,
        list,
    ):
        return payload

    if not isinstance(
        payload,
        dict,
    ):
        raise TipaxPackingSyncError(
            f"ساختار پاسخ {label} معتبر نیست."
        )

    items = payload.get(
        "result"
    )

    if not isinstance(
        items,
        list,
    ):
        raise TipaxPackingSyncError(
            (
                f"لیست result در پاسخ "
                f"{label} پیدا نشد."
            )
        )

    # اگر API اعلام کرده چند رکورد دارد،
    # از Sync پاسخ ناقص جلوگیری می‌کنیم.
    total_count = payload.get(
        "totalCount"
    )

    if total_count is not None:

        try:
            total_count = int(
                total_count
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise TipaxPackingSyncError(
                (
                    f"totalCount پاسخ "
                    f"{label} معتبر نیست."
                )
            ) from exc

        if total_count != len(
            items
        ):
            raise TipaxPackingSyncError(
                (
                    f"پاسخ {label} ناقص است: "
                    f"totalCount={total_count}, "
                    f"received={len(items)}"
                )
            )

    return items


def _decimal(
    value,
):
    if value in (
        None,
        "",
    ):
        return None

    try:
        return Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise TipaxPackingSyncError(
            (
                f"مقدار عددی نامعتبر "
                f"در PackingPrices: {value}"
            )
        ) from exc


def _to_ascii_digits(
    value,
):
    return str(
        value or ""
    ).translate(
        str.maketrans(
            {
                "۰": "0",
                "۱": "1",
                "۲": "2",
                "۳": "3",
                "۴": "4",
                "۵": "5",
                "۶": "6",
                "۷": "7",
                "۸": "8",
                "۹": "9",
                "٠": "0",
                "١": "1",
                "٢": "2",
                "٣": "3",
                "٤": "4",
                "٥": "5",
                "٦": "6",
                "٧": "7",
                "٨": "8",
                "٩": "9",
            }
        )
    )


# =========================================================
# Packing classification
# =========================================================


def _resolve_kind(
    title,
):
    title = str(
        title or ""
    ).strip()

    Kind = (
        ShippingProviderPackingOption
        .Kind
    )

    if (
        "نیاز به بسته بندی ندارد"
        in title
        or
        "نیاز به بسته‌بندی ندارد"
        in title
    ):
        return Kind.NO_PACKING

    # پاکت حبابدار همچنان Envelope است.
    if "پاکت" in title:
        return Kind.ENVELOPE

    if "فلایر" in title:
        return Kind.FLYER

    if "گونی" in title:
        return Kind.SACK

    # باید قبل از CARTON بررسی شود چون:
    # "نایلون حبابدار معادل کارتن سایز ..."
    if "حبابدار" in title:
        return Kind.BUBBLE

    if "کارتن" in title:
        return Kind.CARTON

    return Kind.OTHER


def _extract_box_number(
    title,
    *,
    kind,
):
    if (
        kind
        !=
        ShippingProviderPackingOption
        .Kind
        .CARTON
    ):
        return None

    title = _to_ascii_digits(
        title
    )

    match = re.search(
        r"سایز\s*(\d+)",
        title,
    )

    if match is None:
        return None

    try:
        value = int(
            match.group(1)
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    return (
        value
        if value > 0
        else None
    )


# =========================================================
# Reference validation
# =========================================================


def _validate_motor_parts_content(
    pack_contents,
):
    target = None

    for item in pack_contents:

        if not isinstance(
            item,
            dict,
        ):
            continue

        try:
            item_id = int(
                item.get("id")
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if item_id == 12:
            target = item
            break

    if target is None:
        raise TipaxPackingSyncError(
            (
                "packageContentId=12 در "
                "PackContentRates پیدا نشد."
            )
        )

    try:
        pack_type = int(
            target.get(
                "packType"
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TipaxPackingSyncError(
            (
                "packType مربوط به "
                "packageContentId=12 معتبر نیست."
            )
        ) from exc

    if pack_type != 20:
        raise TipaxPackingSyncError(
            (
                "packageContentId=12 دیگر "
                "مربوط به packType=20 نیست."
            )
        )

    return target


def _validate_parcel_type(
    parcel_types,
):
    target = None

    for item in parcel_types:

        if not isinstance(
            item,
            dict,
        ):
            continue

        try:
            item_id = int(
                item.get("id")
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if item_id == 5:
            target = item
            break

    if target is None:
        raise TipaxPackingSyncError(
            (
                "parcelTypeId=5 در "
                "ParcelType/Search پیدا نشد."
            )
        )

    if not target.get(
        "isActive",
        True,
    ):
        raise TipaxPackingSyncError(
            (
                "parcelTypeId=5 در Tipax "
                "غیرفعال شده است."
            )
        )

    return target


# =========================================================
# Sync
# =========================================================


def sync_tipax_packing(
    *,
    client=None,
):
    client = (
        client
        or TipaxClient()
    )

    # =====================================================
    # Fetch before transaction
    # =====================================================

    try:
        packing_payload = (
            client.get_packing_prices()
        )

        contents_payload = (
            client.get_pack_content_rates()
        )

        parcel_payload = (
            client.get_parcel_types()
        )

    except TipaxAPIError as exc:
        raise TipaxPackingSyncError(
            (
                "خطا در دریافت Reference Data "
                f"از Tipax: {exc}"
            )
        ) from exc

    packing_items = (
        _extract_items(
            packing_payload,
            label="PackingPrices",
        )
    )

    content_items = (
        _extract_items(
            contents_payload,
            label="PackContentRates",
        )
    )

    if not isinstance(
        parcel_payload,
        list,
    ):
        raise TipaxPackingSyncError(
            (
                "ساختار پاسخ "
                "ParcelType/Search معتبر نیست."
            )
        )

    # =====================================================
    # Validate IDs used by PackagingService
    # =====================================================

    motor_parts_content = (
        _validate_motor_parts_content(
            content_items
        )
    )

    package_parcel_type = (
        _validate_parcel_type(
            parcel_payload
        )
    )

    # =====================================================
    # Stats
    # =====================================================

    stats = {
        "raw_packing_options": len(
            packing_items
        ),
        "valid_packing_options": 0,
        "invalid_packing_options": 0,
        "created": 0,
        "updated": 0,
        "deactivated": 0,
        "cartons": 0,
        "package_content": (
            motor_parts_content
        ),
        "parcel_type": (
            package_parcel_type
        ),
    }

    active_ids = set()

    # =====================================================
    # DB
    # =====================================================

    with transaction.atomic():

        for raw in packing_items:

            if not isinstance(
                raw,
                dict,
            ):
                stats[
                    "invalid_packing_options"
                ] += 1
                continue

            try:
                provider_id = int(
                    raw.get(
                        "id"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                stats[
                    "invalid_packing_options"
                ] += 1
                continue

            title = str(
                raw.get(
                    "title"
                )
                or ""
            ).strip()

            if (
                provider_id <= 0
                or
                not title
            ):
                stats[
                    "invalid_packing_options"
                ] += 1
                continue

            raw_pack_type = raw.get(
                "packType"
            )

            if raw_pack_type in (
                None,
                "",
            ):
                pack_type = None

            else:
                try:
                    pack_type = int(
                        raw_pack_type
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    stats[
                        "invalid_packing_options"
                    ] += 1
                    continue

            kind = _resolve_kind(
                title
            )

            box_number = (
                _extract_box_number(
                    title,
                    kind=kind,
                )
            )

            (
                packing,
                created,
            ) = (
                ShippingProviderPackingOption
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_packing_id=(
                        provider_id
                    ),
                    defaults={
                        "title": title,
                        "kind": kind,
                        "box_number": (
                            box_number
                        ),
                        "pack_type": (
                            pack_type
                        ),

                        "length": _decimal(
                            raw.get(
                                "length"
                            )
                        ),
                        "width": _decimal(
                            raw.get(
                                "width"
                            )
                        ),
                        "height": _decimal(
                            raw.get(
                                "height"
                            )
                        ),

                        "min_weight": _decimal(
                            raw.get(
                                "minWeight"
                            )
                        ),
                        "max_weight": _decimal(
                            raw.get(
                                "maxWeight"
                            )
                        ),

                        "min_length": _decimal(
                            raw.get(
                                "minLength"
                            )
                        ),
                        "max_length": _decimal(
                            raw.get(
                                "maxLength"
                            )
                        ),

                        "min_width": _decimal(
                            raw.get(
                                "minWidth"
                            )
                        ),
                        "max_width": _decimal(
                            raw.get(
                                "maxWidth"
                            )
                        ),

                        "min_height": _decimal(
                            raw.get(
                                "minHeight"
                            )
                        ),
                        "max_height": _decimal(
                            raw.get(
                                "maxHeight"
                            )
                        ),

                        "provider_price": (
                            _decimal(
                                raw.get(
                                    "price"
                                )
                            )
                        ),

                        "is_active": True,
                        "raw_data": raw,
                    },
                )
            )

            active_ids.add(
                provider_id
            )

            stats[
                "valid_packing_options"
            ] += 1

            if created:
                stats[
                    "created"
                ] += 1

            else:
                stats[
                    "updated"
                ] += 1

            if (
                kind
                ==
                ShippingProviderPackingOption
                .Kind
                .CARTON
            ):
                stats[
                    "cartons"
                ] += 1

        # =================================================
        # Deactivate options removed from provider
        # =================================================

        stats[
            "deactivated"
        ] = (
            ShippingProviderPackingOption
            .objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_packing_id__in=(
                    active_ids
                )
            )
            .update(
                is_active=False
            )
        )

    return stats