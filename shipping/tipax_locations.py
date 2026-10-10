from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

from django.db import transaction

from addresses.models import City, Province

from shipping.models import (
    ShippingMethod,
    ShippingProviderCity,
    ShippingProviderCityMap,
    ShippingProviderProvince,
    ShippingProviderProvinceMap,
)
from shipping.providers.tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


PROVIDER = ShippingMethod.Provider.TIPAX


class TipaxLocationSyncError(Exception):
    pass


# =========================================================
# Normalize
# =========================================================


def normalize_location_name(value):
    value = unicodedata.normalize(
        "NFKC",
        str(value or ""),
    )

    value = value.translate(
        str.maketrans(
            {
                "ي": "ی",
                "ك": "ک",
                "ة": "ه",
                "ۀ": "ه",
            }
        )
    )

    value = (
        value
        .replace("\u200c", " ")
        .replace("\u200f", " ")
        .replace("\u200e", " ")
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    return value


def location_key(value):
    """
    برای Match کردن اختلاف‌هایی مثل:

        سیستان وبلوچستان
        سیستان و بلوچستان

    یا:
        بندر عباس
        بندرعباس
    """

    value = normalize_location_name(
        value
    )

    if value.startswith("استان "):
        value = value[6:].strip()

    return (
        value
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


# =========================================================
# Generic response helpers
# =========================================================


def first_value(data, *keys):
    if not isinstance(data, dict):
        return None

    for key in keys:
        value = data.get(key)

        if value not in (
            None,
            "",
        ):
            return value

    return None


def extract_items(payload, *keys):
    """
    Tipax ممکن است مستقیم List برگرداند:

        [...]

    یا:

        {"data": [...]}

    یا:

        {
            "data": {
                "items": [...]
            }
        }
    """

    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        raise TipaxLocationSyncError(
            "ساختار پاسخ Tipax معتبر نیست."
        )

    for key in keys:
        value = payload.get(key)

        if isinstance(value, list):
            return value

    for wrapper in (
        "data",
        "result",
    ):
        container = payload.get(
            wrapper
        )

        if isinstance(container, list):
            return container

        if isinstance(container, dict):
            for key in keys:
                value = container.get(
                    key
                )

                if isinstance(
                    value,
                    list,
                ):
                    return value

    raise TipaxLocationSyncError(
        "لیست Locations در پاسخ Tipax پیدا نشد."
    )


def safe_decimal(value):
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
    ):
        return None


# =========================================================
# Local lookup helpers
# =========================================================


def build_province_lookup():
    result = {}

    for province in Province.objects.all():
        result[
            location_key(
                province.name
            )
        ] = province

    return result


def build_city_lookup():
    result = {}

    queryset = (
        City.objects
        .select_related("province")
        .all()
    )

    for city in queryset:
        key = (
            city.province_id,
            location_key(
                city.name
            ),
        )

        result[key] = city

    return result


# =========================================================
# Main Sync
# =========================================================


def sync_tipax_locations(
    *,
    client=None,
):
    client = (
        client
        or TipaxClient()
    )

    # =====================================================
    # Fetch remote data BEFORE transaction
    # =====================================================

    try:
        states_response = (
            client.get_states()
        )

        cities_response = (
            client.get_cities()
        )

    except TipaxAPIError as exc:
        raise TipaxLocationSyncError(
            (
                "خطا در دریافت استان/شهر "
                f"از Tipax: {exc}"
            )
        ) from exc

    states = extract_items(
        states_response,
        "states",
        "stateList",
        "items",
    )

    cities = extract_items(
        cities_response,
        "cities",
        "cityList",
        "items",
    )

    # =====================================================
    # Statistics
    # =====================================================

    stats = {
        "raw_states": len(
            states
        ),
        "raw_cities": len(
            cities
        ),

        "valid_states": 0,
        "invalid_states": 0,

        "valid_cities": 0,
        "invalid_cities": 0,

        "unknown_state_cities": 0,

        "province_created": 0,
        "province_existing": 0,

        "city_created": 0,
        "city_existing": 0,

        "provider_province_created": 0,
        "provider_province_updated": 0,

        "provider_city_created": 0,
        "provider_city_updated": 0,

        "province_map_created": 0,
        "province_map_updated": 0,

        "city_map_created": 0,
        "city_map_updated": 0,

        "skipped_cities": [],
    }

    province_lookup = (
        build_province_lookup()
    )

    city_lookup = (
        build_city_lookup()
    )

    # Tipax stateId → local Province
    remote_state_to_local = {}

    active_state_ids = set()
    active_city_ids = set()

    # =====================================================
    # Database
    # =====================================================

    with transaction.atomic():

        # =================================================
        # States / Provinces
        # =================================================

        for raw_state in states:

            if not isinstance(
                raw_state,
                dict,
            ):
                stats[
                    "invalid_states"
                ] += 1

                continue

            remote_state_id = (
                first_value(
                    raw_state,
                    "id",
                    "stateId",
                    "provinceId",
                )
            )

            state_name = first_value(
                raw_state,
                "title",
                "name",
                "stateTitle",
                "stateName",
                "provinceTitle",
                "provinceName",
            )

            if (
                remote_state_id
                in (
                    None,
                    "",
                )
                or
                not state_name
            ):
                stats[
                    "invalid_states"
                ] += 1

                continue

            try:
                remote_state_id_int = int(
                    remote_state_id
                )

            except (
                TypeError,
                ValueError,
            ):
                stats[
                    "invalid_states"
                ] += 1

                continue

            remote_state_id_str = str(
                remote_state_id_int
            )

            state_name = (
                normalize_location_name(
                    state_name
                )
            )

            # ---------------------------------------------
            # Provider Province Catalog
            # ---------------------------------------------

            (
                provider_province,
                provider_created,
            ) = (
                ShippingProviderProvince
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_province_id=(
                        remote_state_id_str
                    ),
                    defaults={
                        "name": (
                            state_name
                        ),
                        "is_active": True,
                        "raw_data": (
                            raw_state
                        ),
                    },
                )
            )

            if provider_created:
                stats[
                    "provider_province_created"
                ] += 1

            else:
                stats[
                    "provider_province_updated"
                ] += 1

            # ---------------------------------------------
            # Local Province
            # ---------------------------------------------

            key = location_key(
                state_name
            )

            local_province = (
                province_lookup.get(
                    key
                )
            )

            if local_province is None:

                local_province = (
                    Province.objects.create(
                        name=state_name
                    )
                )

                province_lookup[
                    key
                ] = local_province

                stats[
                    "province_created"
                ] += 1

            else:
                stats[
                    "province_existing"
                ] += 1

            # ---------------------------------------------
            # Provider Province Map
            # ---------------------------------------------

            (
                province_map,
                map_created,
            ) = (
                ShippingProviderProvinceMap
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_province_id=(
                        remote_state_id_str
                    ),
                    defaults={
                        "province": (
                            local_province
                        ),
                        "provider_province_name": (
                            state_name
                        ),
                        "is_active": True,
                    },
                )
            )

            if map_created:
                stats[
                    "province_map_created"
                ] += 1

            else:
                stats[
                    "province_map_updated"
                ] += 1

            remote_state_to_local[
                remote_state_id_str
            ] = local_province

            active_state_ids.add(
                remote_state_id_str
            )

            stats[
                "valid_states"
            ] += 1

        # =================================================
        # Cities
        # =================================================

        for raw_city in cities:

            if not isinstance(
                raw_city,
                dict,
            ):
                stats[
                    "invalid_cities"
                ] += 1

                continue

            remote_city_id = first_value(
                raw_city,
                "id",
                "cityId",
            )

            city_name = first_value(
                raw_city,
                "title",
                "name",
                "cityTitle",
                "cityName",
            )

            remote_state_id = (
                first_value(
                    raw_city,
                    "stateId",
                    "provinceId",
                )
            )

            # ---------------------------------------------
            # Invalid system/non-location records
            # ---------------------------------------------

            if (
                remote_city_id
                in (
                    None,
                    "",
                )
                or
                not city_name
                or
                remote_state_id
                in (
                    None,
                    "",
                )
            ):
                stats[
                    "invalid_cities"
                ] += 1

                if (
                    len(
                        stats[
                            "skipped_cities"
                        ]
                    )
                    < 20
                ):
                    stats[
                        "skipped_cities"
                    ].append(
                        raw_city
                    )

                continue

            try:
                remote_city_id_int = int(
                    remote_city_id
                )

                remote_state_id_int = int(
                    remote_state_id
                )

            except (
                TypeError,
                ValueError,
            ):
                stats[
                    "invalid_cities"
                ] += 1

                continue

            remote_city_id_str = str(
                remote_city_id_int
            )

            remote_state_id_str = str(
                remote_state_id_int
            )

            city_name = (
                normalize_location_name(
                    city_name
                )
            )

            # ---------------------------------------------
            # Provider City Catalog
            # ---------------------------------------------

            (
                provider_city,
                provider_created,
            ) = (
                ShippingProviderCity
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_city_id=(
                        remote_city_id_str
                    ),
                    defaults={
                        "provider_province_id": (
                            remote_state_id_str
                        ),
                        "name": city_name,
                        "provider_uuid": str(
                            first_value(
                                raw_city,
                                "jetId",
                                "uuid",
                                "cityUuid",
                            )
                            or ""
                        ),
                        "latitude": (
                            safe_decimal(
                                first_value(
                                    raw_city,
                                    "latitude",
                                    "lat",
                                )
                            )
                        ),
                        "longitude": (
                            safe_decimal(
                                first_value(
                                    raw_city,
                                    "longitude",
                                    "lng",
                                    "lon",
                                )
                            )
                        ),
                        "is_active": True,
                        "raw_data": (
                            raw_city
                        ),
                    },
                )
            )

            if provider_created:
                stats[
                    "provider_city_created"
                ] += 1

            else:
                stats[
                    "provider_city_updated"
                ] += 1

            # ---------------------------------------------
            # Local Province
            # ---------------------------------------------

            local_province = (
                remote_state_to_local.get(
                    remote_state_id_str
                )
            )

            if local_province is None:
                stats[
                    "unknown_state_cities"
                ] += 1

                continue

            # ---------------------------------------------
            # Local City
            # ---------------------------------------------

            local_city_key = (
                local_province.id,
                location_key(
                    city_name
                ),
            )

            local_city = (
                city_lookup.get(
                    local_city_key
                )
            )

            if local_city is None:

                local_city = (
                    City.objects.create(
                        province=(
                            local_province
                        ),
                        name=city_name,
                    )
                )

                city_lookup[
                    local_city_key
                ] = local_city

                stats[
                    "city_created"
                ] += 1

            else:
                stats[
                    "city_existing"
                ] += 1

            # ---------------------------------------------
            # Provider City Map
            # ---------------------------------------------

            (
                city_map,
                map_created,
            ) = (
                ShippingProviderCityMap
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_city_id=(
                        remote_city_id_int
                    ),
                    defaults={
                        "city": local_city,
                        "provider_city_name": (
                            city_name
                        ),
                        "is_active": True,
                    },
                )
            )

            if map_created:
                stats[
                    "city_map_created"
                ] += 1

            else:
                stats[
                    "city_map_updated"
                ] += 1

            active_city_ids.add(
                remote_city_id_int
            )

            stats[
                "valid_cities"
            ] += 1

        # =================================================
        # Deactivate removed Tipax locations
        # =================================================

        (
            ShippingProviderProvince
            .objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_province_id__in=(
                    active_state_ids
                )
            )
            .update(
                is_active=False
            )
        )

        (
            ShippingProviderProvinceMap
            .objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_province_id__in=(
                    active_state_ids
                )
            )
            .update(
                is_active=False
            )
        )

        (
            ShippingProviderCity
            .objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_city_id__in=[
                    str(value)
                    for value
                    in active_city_ids
                ]
            )
            .update(
                is_active=False
            )
        )

        (
            ShippingProviderCityMap
            .objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_city_id__in=(
                    active_city_ids
                )
            )
            .update(
                is_active=False
            )
        )

    return stats