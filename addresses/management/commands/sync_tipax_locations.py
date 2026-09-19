import json
import re

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from django.db import transaction

from addresses.models import (
    City,
    Province,
)

from shipping.providers.tipax_client import (
    TipaxClient,
    TipaxRequestError,
)


# =========================================================
# Exceptions
# =========================================================


class TipaxLocationPayloadError(
    Exception
):
    pass


# =========================================================
# Normalization
# =========================================================


def normalize_location_name(
    value,
):
    """
    نرمال‌سازی نام شهر و استان.

    مثال:
        ي -> ی
        ك -> ک
        حذف فاصله‌های اضافی
        تبدیل نیم‌فاصله به فاصله
    """

    value = str(
        value or ""
    ).strip()

    value = (
        value
        .replace(
            "ي",
            "ی",
        )
        .replace(
            "ك",
            "ک",
        )
        .replace(
            "\u200c",
            " ",
        )
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# =========================================================
# Generic Helpers
# =========================================================


def first_value(
    mapping,
    keys,
):
    """
    اولین مقدار معتبر از بین چند Key احتمالی.
    """

    if not isinstance(
        mapping,
        dict,
    ):
        return None

    # -----------------------------------------------------
    # Exact Match
    # -----------------------------------------------------

    for key in keys:

        if key in mapping:

            value = mapping.get(
                key
            )

            if value not in (
                None,
                "",
            ):

                return value

    # -----------------------------------------------------
    # Case Insensitive Match
    # -----------------------------------------------------

    lower_map = {
        str(key).lower(): value
        for key, value
        in mapping.items()
    }

    for key in keys:

        value = lower_map.get(
            str(key).lower()
        )

        if value not in (
            None,
            "",
        ):

            return value

    return None


def extract_items(
    payload,
):
    """
    استخراج List از Responseهای مختلف Tipax.

    پشتیبانی از:

        [...]
        {"data": [...]}
        {"result": [...]}
        {"items": [...]}
        {"value": [...]}
    """

    # -----------------------------------------------------
    # Direct List
    # -----------------------------------------------------

    if isinstance(
        payload,
        list,
    ):

        return payload

    # -----------------------------------------------------
    # Must Be Dict
    # -----------------------------------------------------

    if not isinstance(
        payload,
        dict,
    ):

        raise TipaxLocationPayloadError(
            (
                "ساختار پاسخ Tipax "
                "نه list است و نه dict."
            )
        )

    # -----------------------------------------------------
    # Common Wrappers
    # -----------------------------------------------------

    for key in (
        "data",
        "result",
        "items",
        "value",
        "cities",
        "Cities",
        "states",
        "States",
    ):

        value = payload.get(
            key
        )

        # Direct nested list
        if isinstance(
            value,
            list,
        ):

            return value

        # Nested wrapper
        if isinstance(
            value,
            dict,
        ):

            for nested_key in (
                "items",
                "data",
                "result",
                "cities",
                "states",
            ):

                nested = value.get(
                    nested_key
                )

                if isinstance(
                    nested,
                    list,
                ):

                    return nested

    raise TipaxLocationPayloadError(
        (
            "هیچ لیستی داخل پاسخ "
            "Tipax پیدا نشد."
        )
    )


# =========================================================
# Parse State
# =========================================================


def parse_tipax_state(
    raw,
):
    """
    Response مورد انتظار State:

        {
            "title": "مازندران",
            "id": 1026
        }

    ولی چند نام جایگزین هم پشتیبانی می‌کنیم.
    """

    if not isinstance(
        raw,
        dict,
    ):

        return None

    # -----------------------------------------------------
    # ID
    # -----------------------------------------------------

    state_id = first_value(
        raw,
        (
            "id",
            "Id",
            "stateId",
            "StateId",
            "provinceId",
            "ProvinceId",
        ),
    )

    # -----------------------------------------------------
    # Name
    # -----------------------------------------------------

    state_name = first_value(
        raw,
        (
            "title",
            "Title",
            "name",
            "Name",
            "stateName",
            "StateName",
            "provinceName",
            "ProvinceName",
        ),
    )

    state_name = (
        normalize_location_name(
            state_name
        )
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if (
        state_id is None
        or not state_name
    ):

        return None

    try:

        state_id = int(
            state_id
        )

    except (
        TypeError,
        ValueError,
    ):

        return None

    return {
        "state_id": state_id,
        "state_name": state_name,
        "raw": raw,
    }


# =========================================================
# Parse City
# =========================================================


def parse_tipax_city(
    raw,
):
    """
    ساختار واقعی مشاهده‌شده Tipax:

        {
            "title": "گلوگاه",
            "stateId": 1026,
            "id": 1899,
            ...
        }
    """

    if not isinstance(
        raw,
        dict,
    ):

        return None

    # -----------------------------------------------------
    # City ID
    # -----------------------------------------------------

    city_id = first_value(
        raw,
        (
            "id",
            "Id",
            "cityId",
            "CityId",
        ),
    )

    # -----------------------------------------------------
    # City Name
    # -----------------------------------------------------

    city_name = first_value(
        raw,
        (
            "title",
            "Title",
            "name",
            "Name",
            "cityName",
            "CityName",
        ),
    )

    # -----------------------------------------------------
    # State ID
    # -----------------------------------------------------

    state_id = first_value(
        raw,
        (
            "stateId",
            "StateId",
            "provinceId",
            "ProvinceId",
        ),
    )

    city_name = (
        normalize_location_name(
            city_name
        )
    )

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if (
        not city_name
        or state_id is None
    ):

        return None

    try:

        state_id = int(
            state_id
        )

    except (
        TypeError,
        ValueError,
    ):

        return None

    try:

        city_id = (
            int(city_id)
            if city_id is not None
            else None
        )

    except (
        TypeError,
        ValueError,
    ):

        city_id = None

    return {
        "city_id": city_id,
        "city_name": city_name,
        "state_id": state_id,
        "raw": raw,
    }


# =========================================================
# Django Command
# =========================================================


class Command(
    BaseCommand
):

    help = (
        "دریافت استان‌ها و شهرها از Tipax "
        "و Sync با addresses.Province/City"
    )

    # =====================================================
    # Arguments
    # =====================================================

    def add_arguments(
        self,
        parser,
    ):

        parser.add_argument(
            "--inspect",
            action="store_true",
            help=(
                "نمونه State و Cityهای Tipax "
                "را نمایش می‌دهد و DB تغییر نمی‌کند."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Sync را اجرا می‌کند ولی "
                "در پایان Transaction Rollback می‌شود."
            ),
        )

        parser.add_argument(
            "--sample-size",
            type=int,
            default=5,
            help=(
                "تعداد رکورد نمونه "
                "برای حالت inspect."
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

        inspect_only = options[
            "inspect"
        ]

        dry_run = options[
            "dry_run"
        ]

        sample_size = max(
            int(
                options[
                    "sample_size"
                ]
            ),
            1,
        )

        client = TipaxClient()

        # =================================================
        # Fetch States
        # =================================================

        self.stdout.write(
            (
                "در حال دریافت "
                "States از Tipax..."
            )
        )

        try:

            states_payload = (
                client.get_states()
            )

        except TipaxRequestError as exc:

            raise CommandError(
                (
                    "دریافت Stateهای "
                    "Tipax ناموفق بود: "
                    f"{exc}"
                )
            ) from exc

        # =================================================
        # Fetch Cities
        # =================================================

        self.stdout.write(
            (
                "در حال دریافت "
                "Cities از Tipax..."
            )
        )

        try:

            cities_payload = (
                client.get_cities()
            )

        except TipaxRequestError as exc:

            raise CommandError(
                (
                    "دریافت Cityهای "
                    "Tipax ناموفق بود: "
                    f"{exc}"
                )
            ) from exc

        # =================================================
        # Extract Lists
        # =================================================

        try:

            state_items = (
                extract_items(
                    states_payload
                )
            )

        except TipaxLocationPayloadError as exc:

            raise CommandError(
                (
                    "ساختار پاسخ States "
                    "قابل تشخیص نیست.\n\n"
                    f"{exc}\n\n"
                    "Response:\n"
                    + json.dumps(
                        states_payload,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )[:5000]
                )
            ) from exc

        try:

            city_items = (
                extract_items(
                    cities_payload
                )
            )

        except TipaxLocationPayloadError as exc:

            raise CommandError(
                (
                    "ساختار پاسخ Cities "
                    "قابل تشخیص نیست.\n\n"
                    f"{exc}\n\n"
                    "Response:\n"
                    + json.dumps(
                        cities_payload,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )[:5000]
                )
            ) from exc

        # =================================================
        # Counts
        # =================================================

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"{len(state_items)} "
                    "State خام دریافت شد."
                )
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"{len(city_items)} "
                    "City خام دریافت شد."
                )
            )
        )

        # =================================================
        # Inspect
        # =================================================

        if inspect_only:

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    "نمونه Stateها:"
                )
            )

            self.stdout.write(
                json.dumps(
                    state_items[
                        :sample_size
                    ],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    "نمونه Cityها:"
                )
            )

            self.stdout.write(
                json.dumps(
                    city_items[
                        :sample_size
                    ],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    (
                        "حالت inspect فعال بود؛ "
                        "دیتابیس تغییر نکرد."
                    )
                )
            )

            return

        # =================================================
        # Parse States
        # =================================================

        parsed_states = []
        invalid_states = []

        for raw_state in state_items:

            parsed_state = (
                parse_tipax_state(
                    raw_state
                )
            )

            if parsed_state is None:

                invalid_states.append(
                    raw_state
                )

                continue

            parsed_states.append(
                parsed_state
            )

        # =================================================
        # State Map
        # =================================================

        state_map = {
            state[
                "state_id"
            ]: state[
                "state_name"
            ]
            for state
            in parsed_states
        }

        if not state_map:

            raise CommandError(
                (
                    "هیچ State معتبر "
                    "از Tipax استخراج نشد."
                )
            )

        # =================================================
        # Parse Cities
        # =================================================

        parsed_cities = []

        invalid_cities = []

        unknown_state_cities = []

        for raw_city in city_items:

            parsed_city = (
                parse_tipax_city(
                    raw_city
                )
            )

            # ---------------------------------------------
            # Invalid City
            # ---------------------------------------------

            if parsed_city is None:

                invalid_cities.append(
                    raw_city
                )

                continue

            # ---------------------------------------------
            # Resolve State
            # ---------------------------------------------

            state_name = (
                state_map.get(
                    parsed_city[
                        "state_id"
                    ]
                )
            )

            if not state_name:

                unknown_state_cities.append(
                    parsed_city
                )

                continue

            parsed_city[
                "state_name"
            ] = state_name

            parsed_cities.append(
                parsed_city
            )

        if not parsed_cities:

            raise CommandError(
                (
                    "هیچ City معتبر "
                    "با State قابل شناسایی "
                    "از Tipax استخراج نشد."
                )
            )

        # =================================================
        # Deduplicate Cities
        # =================================================

        unique_cities = {}

        for item in parsed_cities:

            key = (
                normalize_location_name(
                    item[
                        "state_name"
                    ]
                ),
                normalize_location_name(
                    item[
                        "city_name"
                    ]
                ),
            )

            unique_cities[
                key
            ] = item

        parsed_cities = list(
            unique_cities.values()
        )

        # =================================================
        # Counters
        # =================================================

        province_created = 0
        province_existing = 0

        city_created = 0
        city_existing = 0

        # =================================================
        # Sync
        # =================================================

        with transaction.atomic():

            # ---------------------------------------------
            # Existing Provinces
            # ---------------------------------------------

            existing_provinces = {
                normalize_location_name(
                    province.name
                ): province
                for province
                in Province.objects.all()
            }

            # ---------------------------------------------
            # Existing Cities Cache
            # ---------------------------------------------

            existing_cities = {}

            for city in (
                City.objects
                .select_related(
                    "province"
                )
                .all()
            ):

                key = (
                    normalize_location_name(
                        city.province.name
                    ),
                    normalize_location_name(
                        city.name
                    ),
                )

                existing_cities[
                    key
                ] = city

            # ---------------------------------------------
            # Sync
            # ---------------------------------------------

            for item in parsed_cities:

                state_name = item[
                    "state_name"
                ]

                city_name = item[
                    "city_name"
                ]

                # =========================================
                # Province
                # =========================================

                province_key = (
                    normalize_location_name(
                        state_name
                    )
                )

                province = (
                    existing_provinces.get(
                        province_key
                    )
                )

                if province is None:

                    province = (
                        Province.objects.create(
                            name=state_name
                        )
                    )

                    existing_provinces[
                        province_key
                    ] = province

                    province_created += 1

                else:

                    province_existing += 1

                # =========================================
                # City
                # =========================================

                city_key = (
                    province_key,
                    normalize_location_name(
                        city_name
                    ),
                )

                city = (
                    existing_cities.get(
                        city_key
                    )
                )

                if city is not None:

                    city_existing += 1

                    continue

                city = (
                    City.objects.create(
                        province=province,
                        name=city_name,
                    )
                )

                existing_cities[
                    city_key
                ] = city

                city_created += 1

            # =============================================
            # Dry Run
            # =============================================

            if dry_run:

                transaction.set_rollback(
                    True
                )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Sync Tipax Locations "
                    "تمام شد."
                )
            )
        )

        self.stdout.write(
            (
                "Valid states: "
                f"{len(parsed_states)}"
            )
        )

        self.stdout.write(
            (
                "Invalid states: "
                f"{len(invalid_states)}"
            )
        )

        self.stdout.write(
            (
                "Valid cities: "
                f"{len(parsed_cities)}"
            )
        )

        self.stdout.write(
            (
                "Invalid cities: "
                f"{len(invalid_cities)}"
            )
        )

        self.stdout.write(
            (
                "Cities with unknown state: "
                f"{len(unknown_state_cities)}"
            )
        )

        self.stdout.write(
            (
                "Province created: "
                f"{province_created}"
            )
        )

        self.stdout.write(
            (
                "Province existing hits: "
                f"{province_existing}"
            )
        )

        self.stdout.write(
            (
                "City created: "
                f"{city_created}"
            )
        )

        self.stdout.write(
            (
                "City existing: "
                f"{city_existing}"
            )
        )

        # =================================================
        # Invalid Samples
        # =================================================

        if invalid_cities:

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    (
                        "نمونه Cityهای Skip شده:"
                    )
                )
            )

            self.stdout.write(
                json.dumps(
                    invalid_cities[:3],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        if unknown_state_cities:

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    (
                        "نمونه Cityهایی که "
                        "State آنها پیدا نشد:"
                    )
                )
            )

            self.stdout.write(
                json.dumps(
                    unknown_state_cities[:3],
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )

        # =================================================
        # Dry Run Message
        # =================================================

        if dry_run:

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    (
                        "Dry-run فعال بود؛ "
                        "تمام تغییرات دیتابیس "
                        "Rollback شدند."
                    )
                )
            )