import re
import unicodedata
from decimal import Decimal, InvalidOperation

from django.db import transaction

from addresses.models import Province, City

from shipping.models import (
    ShippingMethod,
    ShippingProviderProvince,
    ShippingProviderProvinceMap,
    ShippingProviderCity,
    ShippingProviderCityMap,
)

from shipping.providers.tipax_client import (
    TipaxClient,
    TipaxAPIError,
)


class TipaxLocationSyncError(Exception):
    pass


PROVIDER = ShippingMethod.Provider.TIPAX


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
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    return value


def normalize_province_name(value):
    value = normalize_location_name(value)

    if value.startswith("استان "):
        value = value[6:].strip()

    return value


# =========================================================
# Helpers
# =========================================================


def _first_value(data, *keys):
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


def _extract_items(payload, keys):
    """
    پاسخ‌های مختلف Tipax را تحمل می‌کند:

    [...]
    {"data": [...]}
    {"data": {"cities": [...]}}
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

    for container_key in (
        "data",
        "result",
    ):
        container = payload.get(
            container_key
        )

        if isinstance(container, list):
            return container

        if isinstance(container, dict):
            for key in keys:
                value = container.get(key)

                if isinstance(value, list):
                    return value

    raise TipaxLocationSyncError(
        "لیست Location در پاسخ Tipax پیدا نشد."
    )


def _to_decimal(value):
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
# Province Helpers
# =========================================================


def _find_local_province(name):
    normalized = normalize_province_name(
        name
    )

    for province in Province.objects.all():
        if (
            normalize_province_name(
                province.name
            )
            == normalized
        ):
            return province

    return None


def _resolve_local_province(
    *,
    provider_id,
    provider_name,
):
    existing_map = (
        ShippingProviderProvinceMap.objects
        .select_related("province")
        .filter(
            provider=PROVIDER,
            provider_province_id=str(
                provider_id
            ),
        )
        .first()
    )

    if existing_map:
        if not existing_map.is_active:
            existing_map.is_active = True
            existing_map.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )

        return existing_map.province

    province = _find_local_province(
        provider_name
    )

    if province is None:
        province = Province.objects.create(
            name=normalize_location_name(
                provider_name
            )
        )

    ShippingProviderProvinceMap.objects.update_or_create(
        provider=PROVIDER,
        province=province,
        defaults={
            "provider_province_id": str(
                provider_id
            ),
            "provider_province_name": (
                provider_name
            ),
            "is_active": True,
        },
    )

    return province


# =========================================================
# City Helpers
# =========================================================


def _find_local_city(
    *,
    province,
    name,
):
    normalized = normalize_location_name(
        name
    )

    for city in City.objects.filter(
        province=province
    ):
        if (
            normalize_location_name(
                city.name
            )
            == normalized
        ):
            return city

    return None


def _resolve_local_city(
    *,
    provider_city_id,
    provider_city_name,
    local_province,
):
    existing_map = (
        ShippingProviderCityMap.objects
        .select_related(
            "city",
            "city__province",
        )
        .filter(
            provider=PROVIDER,
            provider_city_id=int(
                provider_city_id
            ),
        )
        .first()
    )

    if existing_map:
        if (
            existing_map.city.province_id
            != local_province.id
        ):
            raise TipaxLocationSyncError(
                (
                    f"شهر {provider_city_name} "
                    "قبلاً به استان دیگری Map شده است."
                )
            )

        existing_map.provider_city_name = (
            provider_city_name
        )
        existing_map.is_active = True

        existing_map.save(
            update_fields=[
                "provider_city_name",
                "is_active",
                "updated_at",
            ]
        )

        return existing_map.city

    city = _find_local_city(
        province=local_province,
        name=provider_city_name,
    )

    if city is None:
        city = City.objects.create(
            province=local_province,
            name=normalize_location_name(
                provider_city_name
            ),
        )

    ShippingProviderCityMap.objects.update_or_create(
        provider=PROVIDER,
        city=city,
        defaults={
            "provider_city_id": int(
                provider_city_id
            ),
            "provider_city_name": (
                provider_city_name
            ),
            "is_active": True,
        },
    )

    return city


# =========================================================
# Sync
# =========================================================


def sync_tipax_locations(
    *,
    client=None,
):
    client = client or TipaxClient()

    try:
        states_response = (
            client.get_states()
        )

        cities_response = (
            client.get_cities()
        )

    except TipaxAPIError as exc:
        raise TipaxLocationSyncError(
            f"خطا در دریافت Locations از Tipax: {exc}"
        ) from exc

    states = _extract_items(
        states_response,
        (
            "states",
            "stateList",
            "items",
        ),
    )

    cities = _extract_items(
        cities_response,
        (
            "cities",
            "cityList",
            "items",
        ),
    )

    if not states:
        raise TipaxLocationSyncError(
            "Tipax هیچ استانی برنگرداند."
        )

    if not cities:
        raise TipaxLocationSyncError(
            "Tipax هیچ شهری برنگرداند."
        )

    stats = {
        "provinces": 0,
        "cities": 0,
        "province_maps": 0,
        "city_maps": 0,
        "skipped_cities": 0,
    }

    active_province_ids = set()
    active_city_ids = set()

    province_map = {}

    with transaction.atomic():

        # =================================================
        # Provinces
        # =================================================

        for state in states:
            if not isinstance(
                state,
                dict,
            ):
                continue

            provider_id = _first_value(
                state,
                "id",
                "stateId",
                "provinceId",
            )

            name = _first_value(
                state,
                "name",
                "stateName",
                "provinceName",
                "title",
            )

            if (
                provider_id is None
                or not name
            ):
                continue

            provider_id = str(
                provider_id
            )

            name = normalize_location_name(
                name
            )

            ShippingProviderProvince.objects.update_or_create(
                provider=PROVIDER,
                provider_province_id=provider_id,
                defaults={
                    "name": name,
                    "is_active": True,
                    "raw_data": state,
                },
            )

            local_province = (
                _resolve_local_province(
                    provider_id=provider_id,
                    provider_name=name,
                )
            )

            province_map[
                provider_id
            ] = local_province

            active_province_ids.add(
                provider_id
            )

            stats["provinces"] += 1
            stats["province_maps"] += 1

        # =================================================
        # Cities
        # =================================================

        for city_data in cities:
            if not isinstance(
                city_data,
                dict,
            ):
                continue

            provider_city_id = _first_value(
                city_data,
                "id",
                "cityId",
            )

            provider_province_id = _first_value(
                city_data,
                "stateId",
                "provinceId",
                "state_id",
            )

            name = _first_value(
                city_data,
                "name",
                "cityName",
                "title",
            )

            if (
                provider_city_id is None
                or provider_province_id is None
                or not name
            ):
                stats[
                    "skipped_cities"
                ] += 1
                continue

            provider_city_id = str(
                provider_city_id
            )

            provider_province_id = str(
                provider_province_id
            )

            name = normalize_location_name(
                name
            )

            ShippingProviderCity.objects.update_or_create(
                provider=PROVIDER,
                provider_city_id=(
                    provider_city_id
                ),
                defaults={
                    "provider_province_id": (
                        provider_province_id
                    ),
                    "name": name,
                    "provider_uuid": str(
                        _first_value(
                            city_data,
                            "uuid",
                            "cityUuid",
                        )
                        or ""
                    ),
                    "latitude": _to_decimal(
                        _first_value(
                            city_data,
                            "latitude",
                            "lat",
                        )
                    ),
                    "longitude": _to_decimal(
                        _first_value(
                            city_data,
                            "longitude",
                            "lng",
                            "lon",
                        )
                    ),
                    "is_active": True,
                    "raw_data": city_data,
                },
            )

            local_province = (
                province_map.get(
                    provider_province_id
                )
            )

            if local_province is None:
                stats[
                    "skipped_cities"
                ] += 1
                continue

            _resolve_local_city(
                provider_city_id=(
                    provider_city_id
                ),
                provider_city_name=name,
                local_province=(
                    local_province
                ),
            )

            active_city_ids.add(
                provider_city_id
            )

            stats["cities"] += 1
            stats["city_maps"] += 1

        # =================================================
        # Deactivate removed provider locations
        # =================================================

        (
            ShippingProviderProvince.objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_province_id__in=(
                    active_province_ids
                )
            )
            .update(
                is_active=False
            )
        )

        (
            ShippingProviderProvinceMap.objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_province_id__in=(
                    active_province_ids
                )
            )
            .update(
                is_active=False
            )
        )

        (
            ShippingProviderCity.objects
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

        (
            ShippingProviderCityMap.objects
            .filter(
                provider=PROVIDER
            )
            .exclude(
                provider_city_id__in=[
                    int(value)
                    for value
                    in active_city_ids
                ]
            )
            .update(
                is_active=False
            )
        )

    return stats