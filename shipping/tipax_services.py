from django.db import (
    models,
    transaction,
)
from django.db.models import Q
from django.utils import timezone

from addresses.models import City

from orders.models import Order

from .models import (
    Shipment,
    ShippingMethod,
    ShippingProviderCityMap,
    ShippingSettings,
    TipaxPackageProfile,
    TipaxSettings,
)

from .providers.tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


# =========================================================
# Exceptions
# =========================================================


class TipaxShipmentError(Exception):
    """
    خطاهای مربوط به ثبت، رهگیری یا ابطال
    Shipment در Tipax.
    """

    pass


# =========================================================
# Tipax Tracking Status Mapping
# =========================================================
#
# فقط Statusهایی که از مستندات Tipax می‌شناسیم
# Mapping شده‌اند.
#
# Status ناشناخته حذف نمی‌شود؛
# provider_status_id/name همچنان ذخیره می‌شود.
# =========================================================


TIPAX_STATUS_MAP = {

    # در دست جمع‌آوری
    30: Shipment.Status.WAITING_PICKUP,

    # ابطال شده
    34: Shipment.Status.CANCELLED,

    # جمع‌آوری شده
    38: Shipment.Status.COLLECTED,

    # تحویل گیرنده
    50: Shipment.Status.DELIVERED,

    # عودت شده
    51: Shipment.Status.RETURNED,

    # برگشت خورده
    52: Shipment.Status.RETURNED,

    # در حال پردازش
    58: Shipment.Status.PROCESSING,

    # ثبت اولیه
    59: Shipment.Status.REGISTERED,
}


# =========================================================
# Recursive Response Search
# =========================================================


def _find_value(
    payload,
    *keys,
):
    """
    یک Key را بدون وابستگی به Wrapper Response
    در JSON تیپاکس پیدا می‌کند.

    مثال:

    {
        "data": {
            "result": {
                "orderId": 123
            }
        }
    }

    _find_value(..., "orderId")
    """

    wanted_keys = {
        str(key).lower()
        for key in keys
    }

    # =====================================================
    # Dict
    # =====================================================

    if isinstance(
        payload,
        dict,
    ):

        # ابتدا همین Level.
        for key, value in (
            payload.items()
        ):

            if (
                str(key).lower()
                in wanted_keys
            ):

                return value

        # سپس Nested.
        for value in (
            payload.values()
        ):

            result = _find_value(
                value,
                *keys,
            )

            if result is not None:

                return result

    # =====================================================
    # List
    # =====================================================

    elif isinstance(
        payload,
        list,
    ):

        for item in payload:

            result = _find_value(
                item,
                *keys,
            )

            if result is not None:

                return result

    return None


# =========================================================
# Normalize Tracking Codes
# =========================================================


def _normalize_tracking_codes(
    value,
):
    """
    trackingCodes را همیشه به list[str]
    تبدیل می‌کند.
    """

    if value is None:

        return []

    if isinstance(
        value,
        list,
    ):

        return [
            str(item).strip()
            for item in value
            if item is not None
            and str(item).strip()
        ]

    if isinstance(
        value,
        (
            tuple,
            set,
        ),
    ):

        return [
            str(item).strip()
            for item in value
            if item is not None
            and str(item).strip()
        ]

    value = str(
        value
    ).strip()

    if not value:

        return []

    return [
        value
    ]


# =========================================================
# Get Tipax City ID
# =========================================================


def _get_tipax_city_id(
    city,
):
    """
    City داخلی پروژه را به City ID تیپاکس تبدیل می‌کند.
    """

    if city is None:

        raise TipaxShipmentError(
            "شهر برای ارسال تیپاکس مشخص نیست."
        )

    mapping = (
        ShippingProviderCityMap.objects
        .filter(
            provider=(
                ShippingMethod
                .Provider
                .TIPAX
            ),
            city=city,
            is_active=True,
        )
        .first()
    )

    if mapping is None:

        raise TipaxShipmentError(
            (
                f"شهر «{city.name}» هنوز "
                "به City ID تیپاکس متصل نشده است."
            )
        )

    return (
        mapping.provider_city_id
    )


# =========================================================
# Resolve Order Destination City
# =========================================================


def _resolve_order_destination_city(
    order,
):
    """
    مقصد را تا حد امکان بر اساس Snapshot Order
    پیدا می‌کند.

    دلیل:
    ممکن است Address اصلی User بعداً Edit شده باشد.

    اول:
        اگر Address فعلی هنوز با Snapshot مطابقت دارد،
        همان City استفاده می‌شود.

    دوم:
        City از روی Snapshot استان/شهر Order پیدا می‌شود.
    """

    # =====================================================
    # Original Address
    # =====================================================

    if (
        order.address_id
        and order.address
        and order.address.city_id
    ):

        address_city = (
            order.address.city
        )

        address_province = (
            order.address.province
        )

        city_matches = (
            address_city.name
            == order.shipping_city_name
        )

        province_matches = (
            address_province
            and
            address_province.name
            == order.shipping_province_name
        )

        if (
            city_matches
            and province_matches
        ):

            return address_city

    # =====================================================
    # Snapshot Lookup
    # =====================================================

    city = (
        City.objects
        .select_related(
            "province"
        )
        .filter(
            name=(
                order.shipping_city_name
            ),
            province__name=(
                order.shipping_province_name
            ),
        )
        .first()
    )

    if city is None:

        raise TipaxShipmentError(
            (
                "شهر مقصد سفارش بر اساس "
                "Snapshot آدرس پیدا نشد."
            )
        )

    return city


# =========================================================
# Get Package Profile
# =========================================================


def _get_package_profile(
    weight_grams,
):
    """
    Profile مناسب بسته Tipax را بر اساس وزن پیدا می‌کند.
    """

    if (
        weight_grams is None
        or weight_grams <= 0
    ):

        raise TipaxShipmentError(
            "وزن مرسوله نامعتبر است."
        )

    profile = (
        TipaxPackageProfile.objects
        .filter(
            is_active=True,

            min_weight_grams__lte=(
                weight_grams
            ),
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
        .order_by(
            "-priority",
            "min_weight_grams",
            "id",
        )
        .first()
    )

    if profile is None:

        raise TipaxShipmentError(
            (
                "برای وزن این مرسوله "
                "TipaxPackageProfile "
                "تعریف نشده است."
            )
        )

    return profile


# =========================================================
# Get Service ID
# =========================================================


def _get_service_id(
    *,
    shipping_method,
    tipax_settings,
):
    """
    اگر ShippingMethod.service_code عدد باشد،
    همان Service ID تیپاکس استفاده می‌شود.

    در غیر این صورت default_service_id.
    """

    service_code = ""

    if shipping_method:

        service_code = str(
            shipping_method.service_code
            or ""
        ).strip()

    if service_code.isdigit():

        return int(
            service_code
        )

    service_id = (
        tipax_settings
        .default_service_id
    )

    if not service_id:

        raise TipaxShipmentError(
            "Service ID تیپاکس تعریف نشده است."
        )

    return int(
        service_id
    )


# =========================================================
# Validate Tipax Settings
# =========================================================


def _validate_tipax_settings(
    *,
    shipping_settings,
    tipax_settings,
):
    """
    تنظیمات ضروری قبل از Register Shipment.
    """

    errors = []

    # =====================================================
    # Origin
    # =====================================================

    if (
        shipping_settings.origin_city_id
        is None
    ):

        errors.append(
            "شهر مبدا ارسال"
        )

    # =====================================================
    # Sender
    # =====================================================

    if not (
        tipax_settings
        .sender_full_name
        .strip()
    ):

        errors.append(
            "نام فرستنده"
        )

    if not (
        tipax_settings
        .sender_mobile
        .strip()
    ):

        errors.append(
            "موبایل فرستنده"
        )

    if not (
        tipax_settings
        .origin_full_address
        .strip()
    ):

        errors.append(
            "آدرس کامل مبدا"
        )

    if errors:

        raise TipaxShipmentError(
            (
                "تنظیمات تیپاکس ناقص است: "
                +
                "، ".join(
                    errors
                )
            )
        )


# =========================================================
# Build Tipax Order Payload
# =========================================================


def _build_tipax_order_payload(
    *,
    order,
    origin_city_id,
    destination_city_id,
    profile,
    service_id,
    tipax_settings,
    client,
):
    """
    Payload نهایی ثبت Order در Tipax.
    """

    receiver_full_name = (
        (
            f"{order.shipping_first_name} "
            f"{order.shipping_last_name}"
        )
        .strip()
    )

    # ارزش خود کالاهاست؛
    # Shipping و Discount در ارزش فیزیکی مرسوله
    # دخالت داده نمی‌شوند.
    package_value_toman = (
        order.subtotal_toman
    )

    package_value = (
        client.to_tipax_amount(
            package_value_toman
        )
    )

    return {

        # Order Number داخلی ما.
        "traceCode": (
            order.order_number
        ),

        "customerSubstationCode": (
            tipax_settings
            .customer_substation_code
            or ""
        ),

        "packages": [

            {
                # =========================================
                # Origin
                # =========================================

                "origin": {

                    "cityId": (
                        origin_city_id
                    ),

                    "fullAddress": (
                        tipax_settings
                        .origin_full_address
                    ),

                    "floor": (
                        tipax_settings
                        .origin_floor
                        or ""
                    ),

                    "unit": (
                        tipax_settings
                        .origin_unit
                        or ""
                    ),

                    "postalCode": (
                        tipax_settings
                        .origin_postal_code
                        or ""
                    ),

                    "latitude": (
                        tipax_settings
                        .origin_latitude
                        or ""
                    ),

                    "longitude": (
                        tipax_settings
                        .origin_longitude
                        or ""
                    ),

                    "no": (
                        tipax_settings
                        .origin_no
                        or ""
                    ),

                    "description": (
                        tipax_settings
                        .origin_description
                        or ""
                    ),

                    "beneficiary": {

                        "phone": (
                            tipax_settings
                            .sender_phone
                            or ""
                        ),

                        "fullName": (
                            tipax_settings
                            .sender_full_name
                        ),

                        "mobile": (
                            tipax_settings
                            .sender_mobile
                        ),
                    },
                },

                # =========================================
                # Destination
                # =========================================

                "destination": {

                    "cityId": (
                        destination_city_id
                    ),

                    "fullAddress": (
                        order
                        .shipping_postal_address
                    ),

                    # مدل Address فعلی پروژه
                    # Floor / Unit / Plaque جدا ندارد.
                    "floor": "",

                    "unit": "",

                    "postalCode": (
                        order
                        .shipping_postal_code
                        or ""
                    ),

                    "latitude": "",

                    "longitude": "",

                    "no": "",

                    "description": (
                        order.customer_note
                        or ""
                    ),

                    "beneficiary": {

                        "phone": (
                            order
                            .shipping_phone_number
                            or ""
                        ),

                        "fullName": (
                            receiver_full_name
                        ),

                        "mobile": (
                            order
                            .shipping_mobile_number
                        ),
                    },
                },

                # =========================================
                # Package
                # =========================================

                "isUnusual": (
                    profile.is_unusual
                ),

                "weight": (
                    order
                    .shipping_weight_grams
                ),

                "packageValue": (
                    package_value
                ),

                "length": float(
                    profile.length
                ),

                "width": float(
                    profile.width
                ),

                "height": float(
                    profile.height
                ),

                "packingId": (
                    profile.packing_id
                ),

                "packageContentId": (
                    profile
                    .package_content_id
                ),

                # COD محصول نداریم.
                "cod": 0,

                "packType": (
                    profile.pack_type
                ),

                "parcelTypeId": (
                    profile
                    .parcel_type_id
                ),

                "parcelBookId": 0,

                "description": (
                    f"سفارش "
                    f"{order.order_number}"
                ),

                "serviceId": (
                    service_id
                ),

                "enableLabelPrivacy": (
                    tipax_settings
                    .enable_label_privacy
                ),

                "paymentType": (
                    tipax_settings
                    .payment_type
                ),

                "pickupType": (
                    tipax_settings
                    .pickup_type
                ),

                "distributionType": (
                    tipax_settings
                    .distribution_type
                ),

                "cashAmount": 0,

                "barcode": "",

                "customParcelTitle": (
                    order.order_number
                ),
            }
        ],
    }


# =========================================================
# Create Tipax Shipment
# =========================================================


def create_tipax_shipment(
    order,
):
    """
    Order پرداخت‌شده را در Tipax ثبت می‌کند.

    طراحی سه مرحله‌ای:

        DB Lock
            ↓
        Build + Mark registering
            ↓ COMMIT

        HTTP → Tipax

            ↓

        DB Lock
            ↓
        Save orderId/trackingCodes

    بنابراین Network Request هنگام نگه‌داشتن
    Lock دیتابیس انجام نمی‌شود.
    """

    # =====================================================
    # Phase 1
    #
    # Validate + Prepare Shipment
    # =====================================================

    with transaction.atomic():

        order = (
            Order.objects
            .select_for_update()
            .select_related(
                "shipping_method",
                "address",
                "address__province",
                "address__city",
            )
            .get(
                pk=order.pk
            )
        )

        # =================================================
        # Payment
        # =================================================

        if (
            order.payment_status
            != Order.PaymentStatus.PAID
        ):

            raise TipaxShipmentError(
                "سفارش هنوز پرداخت نشده است."
            )

        # =================================================
        # Provider
        # =================================================

        if (
            order.shipping_provider
            != ShippingMethod
            .Provider
            .TIPAX
        ):

            raise TipaxShipmentError(
                "روش ارسال این سفارش تیپاکس نیست."
            )

        # =================================================
        # Existing Shipment
        # =================================================

        existing = (
            Shipment.objects
            .filter(
                order=order,

                provider=(
                    ShippingMethod
                    .Provider
                    .TIPAX
                ),
            )
            .order_by(
                "-created_at"
            )
            .first()
        )

        # قبلاً واقعاً در Tipax ثبت شده.
        if (
            existing
            and
            existing.external_order_id
        ):

            return existing

        # اگر Request دیگری همین الآن در حال
        # ثبت Shipment است، دوباره API را صدا نمی‌زنیم.
        if (
            existing
            and
            existing.provider_status_name
            == "registering"
        ):

            raise TipaxShipmentError(
                (
                    "ثبت مرسوله تیپاکس "
                    "در حال انجام است."
                )
            )

        # =================================================
        # Settings
        # =================================================

        shipping_settings = (
            ShippingSettings.load()
        )

        tipax_settings = (
            TipaxSettings.load()
        )

        _validate_tipax_settings(
            shipping_settings=(
                shipping_settings
            ),
            tipax_settings=(
                tipax_settings
            ),
        )

        # =================================================
        # Cities
        # =================================================

        origin_city = (
            shipping_settings
            .origin_city
        )

        destination_city = (
            _resolve_order_destination_city(
                order
            )
        )

        origin_city_id = (
            _get_tipax_city_id(
                origin_city
            )
        )

        destination_city_id = (
            _get_tipax_city_id(
                destination_city
            )
        )

        # =================================================
        # Package Profile
        # =================================================

        profile = (
            _get_package_profile(
                order
                .shipping_weight_grams
            )
        )

        # =================================================
        # Service
        # =================================================

        service_id = (
            _get_service_id(
                shipping_method=(
                    order
                    .shipping_method
                ),
                tipax_settings=(
                    tipax_settings
                ),
            )
        )

        # =================================================
        # Client
        # =================================================

        client = TipaxClient()

        # =================================================
        # Payload
        # =================================================

        payload = (
            _build_tipax_order_payload(

                order=order,

                origin_city_id=(
                    origin_city_id
                ),

                destination_city_id=(
                    destination_city_id
                ),

                profile=profile,

                service_id=(
                    service_id
                ),

                tipax_settings=(
                    tipax_settings
                ),

                client=client,
            )
        )

        # =================================================
        # Shipment Placeholder
        # =================================================

        if existing:

            shipment = existing

            shipment.request_payload = (
                payload
            )

            shipment.provider_status_name = (
                "registering"
            )

            shipment.save(
                update_fields=[
                    "request_payload",
                    "provider_status_name",
                    "updated_at",
                ]
            )

        else:

            shipment = (
                Shipment.objects.create(

                    order=order,

                    shipping_method=(
                        order.shipping_method
                    ),

                    provider=(
                        ShippingMethod
                        .Provider
                        .TIPAX
                    ),

                    status=(
                        Shipment.Status
                        .CREATED
                    ),

                    quoted_amount_toman=(
                        order
                        .shipping_amount_toman
                    ),

                    request_payload=(
                        payload
                    ),

                    provider_status_name=(
                        "registering"
                    ),
                )
            )

        shipment_id = (
            shipment.pk
        )

    # =====================================================
    # Transaction Commit شد.
    # حالا Network Request.
    # =====================================================


    # =====================================================
    # Phase 2
    #
    # Tipax API Call
    # =====================================================

    try:

        response = (
            client.create_order(
                payload
            )
        )

    except TipaxAPIError as exc:

        # ---------------------------------------------
        # Mark Registration Failure
        # ---------------------------------------------

        with transaction.atomic():

            shipment = (
                Shipment.objects
                .select_for_update()
                .get(
                    pk=shipment_id
                )
            )

            shipment.provider_status_name = (
                "registration_failed"
            )

            shipment.response_payload = {
                "error": str(exc),
            }

            shipment.save(
                update_fields=[
                    "provider_status_name",
                    "response_payload",
                    "updated_at",
                ]
            )

        raise TipaxShipmentError(
            str(exc)
        ) from exc


    # =====================================================
    # Parse Tipax Response
    # =====================================================

    order_id = (
        _find_value(
            response,
            "orderId",
        )
    )

    tracking_codes = (
        _find_value(
            response,
            "trackingCodes",
        )
    )

    final_amount = (
        _find_value(
            response,
            "finalAmount",
        )
    )

    tracking_codes = (
        _normalize_tracking_codes(
            tracking_codes
        )
    )

    # =====================================================
    # Validate Response
    # =====================================================

    if not order_id:

        with transaction.atomic():

            shipment = (
                Shipment.objects
                .select_for_update()
                .get(
                    pk=shipment_id
                )
            )

            shipment.provider_status_name = (
                "registration_failed"
            )

            shipment.response_payload = (
                response
            )

            shipment.save(
                update_fields=[
                    "provider_status_name",
                    "response_payload",
                    "updated_at",
                ]
            )

        raise TipaxShipmentError(
            (
                "Tipax پاسخ ثبت سفارش را "
                "ارسال کرد اما orderId "
                "در پاسخ وجود ندارد."
            )
        )


    # =====================================================
    # Phase 3
    #
    # Save Successful Registration
    # =====================================================

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .select_related(
                "order"
            )
            .get(
                pk=shipment_id
            )
        )

        # ممکن است Callback/Request دیگری
        # در فاصله Network Request Shipment را
        # ثبت کرده باشد.
        if (
            shipment.external_order_id
        ):

            return shipment

        shipment.external_order_id = (
            str(order_id)
        )

        shipment.tracking_codes = (
            tracking_codes
        )

        shipment.primary_tracking_code = (
            tracking_codes[0]
            if tracking_codes
            else ""
        )

        shipment.status = (
            Shipment.Status.REGISTERED
        )

        shipment.provider_status_name = (
            "registered"
        )

        shipment.response_payload = (
            response
        )

        # اگر Tipax مبلغ نهایی واقعی را
        # در Response برگرداند Snapshot می‌کنیم.
        if final_amount is not None:

            try:

                shipment.final_amount_toman = (
                    client.to_toman(
                        final_amount
                    )
                )

            except (
                TypeError,
                ValueError,
                ArithmeticError,
            ):

                # Response اصلی ذخیره شده؛
                # خطای تبدیل مبلغ نباید
                # Shipment موفق را Fail کند.
                pass

        shipment.save(
            update_fields=[
                "external_order_id",
                "tracking_codes",
                "primary_tracking_code",
                "status",
                "provider_status_name",
                "response_payload",
                "final_amount_toman",
                "updated_at",
            ]
        )

    return shipment


# =========================================================
# Track Tipax Shipment
# =========================================================


def track_tipax_shipment(
    shipment,
):
    """
    آخرین وضعیت Shipment را از Tipax دریافت می‌کند.
    """

    # =====================================================
    # Phase 1 - Read
    # =====================================================

    shipment = (
        Shipment.objects
        .select_related(
            "order",
        )
        .get(
            pk=shipment.pk
        )
    )

    if (
        shipment.provider
        != ShippingMethod
        .Provider
        .TIPAX
    ):

        raise TipaxShipmentError(
            "Shipment متعلق به تیپاکس نیست."
        )

    if not (
        shipment
        .primary_tracking_code
    ):

        raise TipaxShipmentError(
            "کد رهگیری تیپاکس وجود ندارد."
        )

    tracking_code = (
        shipment
        .primary_tracking_code
    )

    # =====================================================
    # Phase 2 - API
    # =====================================================

    client = TipaxClient()

    try:

        response = (
            client.brief_tracking(
                tracking_code
            )
        )

    except TipaxAPIError as exc:

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    # =====================================================
    # Parse
    # =====================================================

    status_id = (
        _find_value(
            response,
            "contractStatusId",
            "statusId",
        )
    )

    status_name = (
        _find_value(
            response,
            "contractStatusName",
            "statusName",
            "status",
        )
    )

    numeric_status = None

    if status_id is not None:

        try:

            numeric_status = int(
                status_id
            )

        except (
            TypeError,
            ValueError,
        ):

            numeric_status = None

    # =====================================================
    # Phase 3 - Save
    # =====================================================

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .get(
                pk=shipment.pk
            )
        )

        # ---------------------------------------------
        # Internal Status Mapping
        # ---------------------------------------------

        if (
            numeric_status
            in TIPAX_STATUS_MAP
        ):

            shipment.status = (
                TIPAX_STATUS_MAP[
                    numeric_status
                ]
            )

        # ---------------------------------------------
        # Provider Status
        # ---------------------------------------------

        shipment.provider_status_id = (
            str(status_id)
            if status_id is not None
            else ""
        )

        shipment.provider_status_name = (
            str(status_name)
            if status_name is not None
            else ""
        )

        shipment.tracking_payload = (
            response
        )

        shipment.save(
            update_fields=[
                "status",
                "provider_status_id",
                "provider_status_name",
                "tracking_payload",
                "updated_at",
            ]
        )

    return shipment


# =========================================================
# Track By Tipax Order ID
# =========================================================


def track_tipax_shipment_by_order_id(
    shipment,
):
    """
    رهگیری بر اساس Tipax orderId.

    برای Debug/Reconciliation کاربرد دارد.
    """

    shipment = (
        Shipment.objects
        .get(
            pk=shipment.pk
        )
    )

    if (
        shipment.provider
        != ShippingMethod
        .Provider
        .TIPAX
    ):

        raise TipaxShipmentError(
            "Shipment متعلق به تیپاکس نیست."
        )

    if not shipment.external_order_id:

        raise TipaxShipmentError(
            "Tipax orderId وجود ندارد."
        )

    client = TipaxClient()

    try:

        response = (
            client.track_by_order_id(
                shipment
                .external_order_id
            )
        )

    except TipaxAPIError as exc:

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .get(
                pk=shipment.pk
            )
        )

        shipment.tracking_payload = (
            response
        )

        shipment.save(
            update_fields=[
                "tracking_payload",
                "updated_at",
            ]
        )

    return shipment


# =========================================================
# Cancel Tipax Shipment
# =========================================================


def cancel_tipax_shipment(
    shipment,
):
    """
    Shipment ثبت‌شده در Tipax را ابطال می‌کند.

    توجه:
    Cancel کردن Shipment به معنی Cancel کردن Order
    فروشگاه نیست.

    Order cancellation باید از Order Service انجام شود.
    """

    # =====================================================
    # Phase 1
    # =====================================================

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .select_related(
                "order"
            )
            .get(
                pk=shipment.pk
            )
        )

        if (
            shipment.provider
            != ShippingMethod
            .Provider
            .TIPAX
        ):

            raise TipaxShipmentError(
                "Shipment متعلق به تیپاکس نیست."
            )

        # Idempotent.
        if (
            shipment.status
            == Shipment.Status.CANCELLED
        ):

            return shipment

        if not (
            shipment
            .external_order_id
        ):

            raise TipaxShipmentError(
                "Tipax orderId وجود ندارد."
            )

        # Shipment تحویل‌شده نباید Cancel شود.
        if (
            shipment.status
            == Shipment.Status.DELIVERED
        ):

            raise TipaxShipmentError(
                (
                    "مرسوله تحویل‌شده "
                    "قابل ابطال نیست."
                )
            )

        external_order_id = (
            shipment
            .external_order_id
        )

    # =====================================================
    # Phase 2 - API
    # =====================================================

    client = TipaxClient()

    try:

        response = (
            client.cancel_order(
                external_order_id
            )
        )

    except TipaxAPIError as exc:

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    # =====================================================
    # Phase 3 - Save
    # =====================================================

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .get(
                pk=shipment.pk
            )
        )

        # Request دیگری قبلاً Cancel کرده.
        if (
            shipment.status
            == Shipment.Status.CANCELLED
        ):

            return shipment

        shipment.status = (
            Shipment.Status.CANCELLED
        )

        shipment.provider_status_name = (
            "cancelled"
        )

        shipment.cancelled_at = (
            timezone.now()
        )

        old_response = (
            shipment.response_payload
            if isinstance(
                shipment.response_payload,
                dict,
            )
            else {}
        )

        shipment.response_payload = {
            **old_response,

            "cancel_response": (
                response
            ),
        }

        shipment.save(
            update_fields=[
                "status",
                "provider_status_name",
                "cancelled_at",
                "response_payload",
                "updated_at",
            ]
        )

    return shipment