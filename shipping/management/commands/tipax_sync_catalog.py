from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation

from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from addresses.models import (
    City,
    Province,
)

from shipping.models import (
    ShippingMethod,
    ShippingProviderCity,
    ShippingProviderCityMap,
    ShippingProviderPackingOption,
    ShippingProviderProvince,
    ShippingProviderProvinceMap,
)

from shipping.providers.tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


PROVIDER = ShippingMethod.Provider.TIPAX


# =========================================================
# Text normalization
# =========================================================


def normalize_text(value):
    if value is None:
        return ""

    value = str(value)

    value = value.translate(
        str.maketrans(
            {
                "ي": "ی",
                "ى": "ی",
                "ك": "ک",
                "ة": "ه",
                "ۀ": "ه",
                "\u200c": " ",
                "\u200f": "",
                "\u200e": "",
                "\t": " ",
            }
        )
    )

    value = unicodedata.normalize(
        "NFKC",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip().lower()


# =========================================================
# Persian / Arabic digits
# =========================================================


def normalize_digits(value):
    if value is None:
        return ""

    return str(value).translate(
        str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
    )


# =========================================================
# Safe decimal
# =========================================================


def to_decimal(value):
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
        ValueError,
        TypeError,
    ):
        return None


# =========================================================
# Packing kind
# =========================================================


def detect_packing_kind(title):
    title_normalized = normalize_text(title)

    Kind = ShippingProviderPackingOption.Kind

    # مهم:
    # قبل از CARTON باید انواعی که عبارت «کارتن»
    # داخل عنوانشان دارند بررسی شوند.
    if (
        "حباب" in title_normalized
        or "نایلون حباب" in title_normalized
    ):
        return Kind.BUBBLE

    if "پاکت" in title_normalized:
        return Kind.ENVELOPE

    if "گونی" in title_normalized:
        return Kind.SACK

    if "فلایر" in title_normalized:
        return Kind.FLYER

    if (
        "نیاز به بسته بندی ندارد"
        in title_normalized
    ):
        return Kind.NO_PACKING

    if "کارتن" in title_normalized:
        return Kind.CARTON

    return Kind.OTHER


# =========================================================
# Box number
# =========================================================


def detect_box_number(
    title,
):
    """
    مثال:
        کارتن سایز 1
        کارتن سایز ۱۰
    """

    title = normalize_digits(
        title
    )

    match = re.search(
        r"سایز\s*([0-9]+)",
        title,
    )

    if not match:
        return None

    try:
        return int(
            match.group(1)
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


# =========================================================
# Command
# =========================================================


class Command(BaseCommand):
    help = (
        "Sync Tipax cities, states and "
        "packing catalog and safely map "
        "local locations."
    )

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help=(
                "Mark Tipax catalog records "
                "not returned by API inactive."
            ),
        )

        parser.add_argument(
            "--skip-auto-map",
            action="store_true",
            help=(
                "Sync provider catalog only "
                "without automatic city/province mapping."
            ),
        )

    # =====================================================
    # Handle
    # =====================================================

    def handle(
        self,
        *args,
        **options,
    ):
        self.client = TipaxClient()

        self.deactivate_missing = (
            options[
                "deactivate_missing"
            ]
        )

        self.skip_auto_map = (
            options[
                "skip_auto_map"
            ]
        )

        try:
            packing_payload = (
                self.client
                .get_packing_prices()
            )

            cities_payload = (
                self.client
                .get_cities()
            )

        except TipaxAPIError as exc:
            raise CommandError(
                f"Tipax API error: {exc}"
            ) from exc

        packing_rows = (
            self._extract_packing_rows(
                packing_payload
            )
        )

        city_rows = (
            self._extract_city_rows(
                cities_payload
            )
        )

        self.stdout.write(
            f"Packing rows: "
            f"{len(packing_rows)}"
        )

        self.stdout.write(
            f"City rows: "
            f"{len(city_rows)}"
        )

        with transaction.atomic():

            packing_stats = (
                self._sync_packings(
                    packing_rows
                )
            )

            city_stats = (
                self._sync_cities(
                    city_rows
                )
            )

            province_stats = (
                self._sync_provider_provinces(
                    city_rows
                )
            )

            if self.skip_auto_map:

                map_stats = {
                    "city_mapped": 0,
                    "city_ambiguous": 0,
                    "city_unmatched": 0,
                    "province_mapped": 0,
                    "province_ambiguous": 0,
                }

            else:

                city_map_stats = (
                    self._auto_map_cities()
                )

                province_map_stats = (
                    self._auto_map_provinces()
                )

                map_stats = {
                    **city_map_stats,
                    **province_map_stats,
                }

        self._print_summary(
            packing_stats=packing_stats,
            city_stats=city_stats,
            province_stats=(
                province_stats
            ),
            map_stats=map_stats,
        )

    # =====================================================
    # Extract packing rows
    # =====================================================

    @staticmethod
    def _extract_packing_rows(
        payload,
    ):
        if isinstance(
            payload,
            dict,
        ):
            rows = payload.get(
                "result",
                []
            )

        elif isinstance(
            payload,
            list,
        ):
            rows = payload

        else:
            rows = []

        return [
            row
            for row in rows
            if isinstance(
                row,
                dict,
            )
            and row.get(
                "id"
            )
        ]

    # =====================================================
    # Extract cities
    # =====================================================

    @staticmethod
    def _extract_city_rows(
        payload,
    ):
        if isinstance(
            payload,
            list,
        ):
            rows = payload

        elif isinstance(
            payload,
            dict,
        ):
            rows = (
                payload.get(
                    "result"
                )
                or payload.get(
                    "data"
                )
                or []
            )

        else:
            rows = []

        return [
            row
            for row in rows
            if isinstance(
                row,
                dict,
            )
            and row.get(
                "id"
            )
            and row.get(
                "title"
            )
        ]

    # =====================================================
    # Sync packing catalog
    # =====================================================

    def _sync_packings(
        self,
        rows,
    ):
        created_count = 0
        updated_count = 0

        returned_ids = set()

        for row in rows:

            provider_id = int(
                row["id"]
            )

            returned_ids.add(
                provider_id
            )

            title = str(
                row.get(
                    "title"
                )
                or ""
            ).strip()

            defaults = {
                "title": title,

                "kind": (
                    detect_packing_kind(
                        title
                    )
                ),

                "box_number": (
                    detect_box_number(
                        title
                    )
                ),

                "pack_type": (
                    row.get(
                        "packType"
                    )
                ),

                "length": to_decimal(
                    row.get(
                        "length"
                    )
                ),

                "width": to_decimal(
                    row.get(
                        "width"
                    )
                ),

                "height": to_decimal(
                    row.get(
                        "height"
                    )
                ),

                "min_weight": (
                    to_decimal(
                        row.get(
                            "minWeight"
                        )
                    )
                ),

                "max_weight": (
                    to_decimal(
                        row.get(
                            "maxWeight"
                        )
                    )
                ),

                "min_length": (
                    to_decimal(
                        row.get(
                            "minLength"
                        )
                    )
                ),

                "max_length": (
                    to_decimal(
                        row.get(
                            "maxLength"
                        )
                    )
                ),

                "min_width": (
                    to_decimal(
                        row.get(
                            "minWidth"
                        )
                    )
                ),

                "max_width": (
                    to_decimal(
                        row.get(
                            "maxWidth"
                        )
                    )
                ),

                "min_height": (
                    to_decimal(
                        row.get(
                            "minHeight"
                        )
                    )
                ),

                "max_height": (
                    to_decimal(
                        row.get(
                            "maxHeight"
                        )
                    )
                ),

                "provider_price": (
                    to_decimal(
                        row.get(
                            "price"
                        )
                    )
                ),

                "is_active": True,

                "raw_data": row,
            }

            (
                _obj,
                created,
            ) = (
                ShippingProviderPackingOption
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_packing_id=(
                        provider_id
                    ),
                    defaults=defaults,
                )
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        deactivated_count = 0

        if self.deactivate_missing:

            deactivated_count = (
                ShippingProviderPackingOption
                .objects
                .filter(
                    provider=PROVIDER,
                    is_active=True,
                )
                .exclude(
                    provider_packing_id__in=(
                        returned_ids
                    )
                )
                .update(
                    is_active=False
                )
            )

        return {
            "created": created_count,
            "updated": updated_count,
            "deactivated": (
                deactivated_count
            ),
        }

    # =====================================================
    # Sync city catalog
    # =====================================================

    def _sync_cities(
        self,
        rows,
    ):
        created_count = 0
        updated_count = 0

        returned_ids = set()

        for row in rows:

            provider_city_id = str(
                row["id"]
            )

            returned_ids.add(
                provider_city_id
            )

            state_id = row.get(
                "stateId"
            )

            if state_id is None:
                state_id = ""
            else:
                state_id = str(
                    state_id
                )

            defaults = {
                "provider_province_id": (
                    state_id
                ),

                "name": str(
                    row.get(
                        "title"
                    )
                    or ""
                ).strip(),

                "provider_uuid": str(
                    row.get(
                        "jetId"
                    )
                    or ""
                ).strip(),

                "latitude": (
                    to_decimal(
                        row.get(
                            "latitude"
                        )
                    )
                ),

                "longitude": (
                    to_decimal(
                        row.get(
                            "longitude"
                        )
                    )
                ),

                "is_active": True,

                "raw_data": row,
            }

            (
                _obj,
                created,
            ) = (
                ShippingProviderCity
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_city_id=(
                        provider_city_id
                    ),
                    defaults=defaults,
                )
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        deactivated_count = 0

        if self.deactivate_missing:

            deactivated_count = (
                ShippingProviderCity
                .objects
                .filter(
                    provider=PROVIDER,
                    is_active=True,
                )
                .exclude(
                    provider_city_id__in=(
                        returned_ids
                    )
                )
                .update(
                    is_active=False
                )
            )

        return {
            "created": created_count,
            "updated": updated_count,
            "deactivated": (
                deactivated_count
            ),
        }

    # =====================================================
    # Sync provider states
    # =====================================================

    @staticmethod
    def _sync_provider_provinces(
        rows,
    ):
        state_counter = Counter()

        for row in rows:

            state_id = row.get(
                "stateId"
            )

            if state_id is None:
                continue

            state_counter[
                str(state_id)
            ] += 1

        created_count = 0
        updated_count = 0

        for (
            state_id,
            city_count,
        ) in state_counter.items():

            (
                _obj,
                created,
            ) = (
                ShippingProviderProvince
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    provider_province_id=(
                        state_id
                    ),
                    defaults={
                        # Cities API نام استان
                        # را در این پاسخ نمی‌دهد.
                        # بنابراین اسم ساختگی
                        # تولید نمی‌کنیم.
                        "is_active": True,

                        "raw_data": {
                            "source": (
                                "Tipax Cities API"
                            ),
                            "city_count": (
                                city_count
                            ),
                        },
                    },
                )
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {
            "created": created_count,
            "updated": updated_count,
        }

    # =====================================================
    # Auto map local cities
    # =====================================================

    @staticmethod
    def _auto_map_cities():
        provider_cities = list(
            ShippingProviderCity.objects
            .filter(
                provider=PROVIDER,
                is_active=True,
            )
        )

        provider_by_name = (
            defaultdict(
                list
            )
        )

        for city in provider_cities:

            key = normalize_text(
                city.name
            )

            if key:
                provider_by_name[
                    key
                ].append(
                    city
                )

        local_cities = list(
            City.objects
            .select_related(
                "province"
            )
            .all()
        )

        local_name_counts = Counter(
            normalize_text(
                city.name
            )
            for city in local_cities
        )

        mapped = 0
        ambiguous = 0
        unmatched = 0

        for local_city in local_cities:

            key = normalize_text(
                local_city.name
            )

            # فقط Exact normalized
            # و نام یکتای داخلی.
            if (
                not key
                or local_name_counts[
                    key
                ] != 1
            ):
                ambiguous += 1
                continue

            candidates = (
                provider_by_name.get(
                    key,
                    []
                )
            )

            if not candidates:
                unmatched += 1
                continue

            if len(
                candidates
            ) != 1:
                ambiguous += 1
                continue

            provider_city = (
                candidates[0]
            )

            (
                ShippingProviderCityMap
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    city=local_city,
                    defaults={
                        "provider_city_id": (
                            provider_city
                            .provider_city_id
                        ),
                        "provider_city_name": (
                            provider_city.name
                        ),
                        "is_active": True,
                    },
                )
            )

            mapped += 1

        return {
            "city_mapped": mapped,
            "city_ambiguous": (
                ambiguous
            ),
            "city_unmatched": (
                unmatched
            ),
        }

    # =====================================================
    # Auto map provinces
    # =====================================================

    @staticmethod
    def _auto_map_provinces():
        """
        Province map را از City mapهای قطعی
        نتیجه می‌گیریم.

        فقط اگر تمام Cityهای Match‌شده یک Province
        به یک stateId واحد اشاره کنند، استان Map می‌شود.
        """

        provider_city_by_id = {
            str(
                city.provider_city_id
            ): city
            for city in (
                ShippingProviderCity.objects
                .filter(
                    provider=PROVIDER,
                    is_active=True,
                )
            )
        }

        mapped = 0
        ambiguous = 0

        provinces = (
            Province.objects.all()
        )

        for province in provinces:

            city_maps = (
                ShippingProviderCityMap
                .objects
                .filter(
                    provider=PROVIDER,
                    city__province=province,
                    is_active=True,
                )
                .values_list(
                    "provider_city_id",
                    flat=True,
                )
            )

            state_ids = set()

            for provider_city_id in (
                city_maps
            ):

                provider_city = (
                    provider_city_by_id.get(
                        str(
                            provider_city_id
                        )
                    )
                )

                if not provider_city:
                    continue

                state_id = (
                    provider_city
                    .provider_province_id
                )

                if state_id:
                    state_ids.add(
                        str(
                            state_id
                        )
                    )

            if not state_ids:
                continue

            if len(
                state_ids
            ) != 1:
                ambiguous += 1
                continue

            provider_state_id = (
                next(
                    iter(
                        state_ids
                    )
                )
            )

            (
                ShippingProviderProvinceMap
                .objects
                .update_or_create(
                    provider=PROVIDER,
                    province=province,
                    defaults={
                        "provider_province_id": (
                            provider_state_id
                        ),

                        # نام واقعی استان در
                        # Cities API موجود نیست.
                        "provider_province_name": "",

                        "is_active": True,
                    },
                )
            )

            mapped += 1

        return {
            "province_mapped": (
                mapped
            ),
            "province_ambiguous": (
                ambiguous
            ),
        }

    # =====================================================
    # Summary
    # =====================================================

    def _print_summary(
        self,
        *,
        packing_stats,
        city_stats,
        province_stats,
        map_stats,
    ):
        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "TIPAX SYNC COMPLETE"
            )
        )

        self.stdout.write(
            (
                "Packing: "
                f"created={packing_stats['created']} "
                f"updated={packing_stats['updated']} "
                f"deactivated={packing_stats['deactivated']}"
            )
        )

        self.stdout.write(
            (
                "Cities: "
                f"created={city_stats['created']} "
                f"updated={city_stats['updated']} "
                f"deactivated={city_stats['deactivated']}"
            )
        )

        self.stdout.write(
            (
                "Provider states: "
                f"created={province_stats['created']} "
                f"updated={province_stats['updated']}"
            )
        )

        self.stdout.write(
            (
                "City maps: "
                f"mapped={map_stats['city_mapped']} "
                f"ambiguous={map_stats['city_ambiguous']} "
                f"unmatched={map_stats['city_unmatched']}"
            )
        )

        self.stdout.write(
            (
                "Province maps: "
                f"mapped={map_stats['province_mapped']} "
                f"ambiguous={map_stats['province_ambiguous']}"
            )
        )