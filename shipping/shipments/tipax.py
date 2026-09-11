from decimal import Decimal, InvalidOperation

from django.db import transaction

from orders.models import Order

from shipping.models import Shipment

from shipping.providers.tipax_client import (
    TipaxClient,
    TipaxRequestError,
    TipaxIndeterminateError,
)



from django.utils import timezone
# =========================================================
# Exceptions
# =========================================================


class TipaxShipmentError(Exception):
    """
    خطای business-level مربوط به ساخت Shipment تیپاکس.
    """

    pass

class TipaxShipmentIndeterminateError(
    TipaxShipmentError
):
    """
    نتیجه عملیات لغو Shipment در Tipax نامشخص است.

    در این وضعیت نباید Refund خودکار اجرا شود
    تا وضعیت واقعی Provider بررسی شود.
    """

    pass
# =========================================================
# Helpers
# =========================================================


def _required(
    value,
    message,
):
    if value is None:
        raise TipaxShipmentError(
            message
        )

    if isinstance(value, str):

        value = value.strip()

        if not value:
            raise TipaxShipmentError(
                message
            )

    return value


def _to_float(
    value,
    *,
    field_name,
):
    try:

        return float(
            Decimal(
                str(value)
            )
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:

        raise TipaxShipmentError(
            (
                f"مقدار {field_name} "
                "برای Tipax معتبر نیست."
            )
        ) from exc


# =========================================================
# Receiver
# =========================================================


def build_tipax_receiver(
    order,
):
    full_name = (
        f"{order.shipping_first_name} "
        f"{order.shipping_last_name}"
    ).strip()

    _required(
        full_name,
        "نام گیرنده مشخص نیست.",
    )

    mobile = _required(
        order.shipping_mobile_number,
        "شماره موبایل گیرنده مشخص نیست.",
    )

    receiver = {
        "fullName": full_name,
        "mobile": str(
            mobile
        ).strip(),
    }

    phone = str(
        order.shipping_phone_number
        or ""
    ).strip()

    if phone:

        receiver[
            "phone"
        ] = phone

    return receiver


# =========================================================
# Payload Builder
# =========================================================


def build_tipax_shipment_payload(
    *,
    order,
    client=None,
):
    """
    Payload ساخت Shipment را فقط از Snapshot
    خود Order می‌سازد.

    عمداً از:
        ShippingOrigin فعلی
        Product فعلی
        TipaxSettings فعلی

    استفاده نمی‌کند.
    """

    if client is None:
        client = TipaxClient()

    if order.shipping_provider != "tipax":

        raise TipaxShipmentError(
            "این سفارش مربوط به Tipax نیست."
        )

    provider_data = (
        order.shipping_provider_data
        or {}
    )

    # =====================================================
    # Origin Snapshot
    # =====================================================

    origin = (
        provider_data.get(
            "origin"
        )
        or {}
    )

    origin_id = _required(
        origin.get(
            "provider_address_id"
        ),
        (
            "شناسه آدرس مبدا Tipax "
            "داخل Snapshot سفارش وجود ندارد."
        ),
    )

    # =====================================================
    # Destination Snapshot
    # =====================================================

    destination_snapshot = (
        provider_data.get(
            "destination"
        )
        or {}
    )

    destination_city_id = _required(
        destination_snapshot.get(
            "provider_city_id"
        ),
        (
            "شناسه شهر مقصد Tipax "
            "داخل Snapshot سفارش وجود ندارد."
        ),
    )

    full_address = _required(
        order.shipping_postal_address,
        "آدرس گیرنده مشخص نیست.",
    )

    receiver = (
        build_tipax_receiver(
            order
        )
    )

    destination = {
        "cityId": int(
            destination_city_id
        ),

        "fullAddress": str(
            full_address
        ).strip(),

        "beneficiary": dict(
            receiver
        ),
    }

    postal_code = str(
        order.shipping_postal_code
        or ""
    ).strip()

    if postal_code:

        destination[
            "postalCode"
        ] = postal_code

    # =====================================================
    # Shipment Options Snapshot
    # =====================================================

    shipment_options = (
        provider_data.get(
            "shipment_options"
        )
        or {}
    )

    payment_type = _required(
        shipment_options.get(
            "payment_type"
        ),
        (
            "payment_type در Snapshot "
            "سفارش وجود ندارد."
        ),
    )

    pickup_type = _required(
        shipment_options.get(
            "pickup_type"
        ),
        (
            "pickup_type در Snapshot "
            "سفارش وجود ندارد."
        ),
    )

    distribution_type = _required(
        shipment_options.get(
            "distribution_type"
        ),
        (
            "distribution_type در Snapshot "
            "سفارش وجود ندارد."
        ),
    )

    enable_label_privacy = bool(
        shipment_options.get(
            "enable_label_privacy",
            False,
        )
    )

    # =====================================================
    # Service
    # =====================================================

    service_id = _required(
        provider_data.get(
            "service_id"
        ),
        (
            "service_id در Snapshot "
            "ارسال وجود ندارد."
        ),
    )

    # =====================================================
    # Packages
    # =====================================================

    package_snapshots = (
        provider_data.get(
            "packages"
        )
        or []
    )

    if not package_snapshots:

        raise TipaxShipmentError(
            (
                "اطلاعات بسته‌های ارسال "
                "در Snapshot سفارش وجود ندارد."
            )
        )

    tipax_packages = []

    for index, package in enumerate(
        package_snapshots,
        start=1,
    ):

        dimensions = (
            package.get(
                "dimensions"
            )
            or {}
        )

        weight_grams = _required(
            package.get(
                "weight_grams"
            ),
            (
                f"وزن بسته شماره {index} "
                "مشخص نیست."
            ),
        )

        declared_value_toman = (
            _required(
                package.get(
                    "declared_value_toman"
                ),
                (
                    f"ارزش بسته شماره {index} "
                    "مشخص نیست."
                ),
            )
        )

        packing_id = _required(
            package.get(
                "packing_id"
            ),
            (
                f"packing_id بسته شماره "
                f"{index} مشخص نیست."
            ),
        )

        package_content_id = (
            _required(
                package.get(
                    "package_content_id"
                ),
                (
                    f"package_content_id بسته "
                    f"شماره {index} مشخص نیست."
                ),
            )
        )

        pack_type = _required(
            package.get(
                "pack_type"
            ),
            (
                f"pack_type بسته شماره "
                f"{index} مشخص نیست."
            ),
        )

        length_cm = _required(
            dimensions.get(
                "length_cm"
            ),
            (
                f"طول بسته شماره "
                f"{index} مشخص نیست."
            ),
        )

        width_cm = _required(
            dimensions.get(
                "width_cm"
            ),
            (
                f"عرض بسته شماره "
                f"{index} مشخص نیست."
            ),
        )

        height_cm = _required(
            dimensions.get(
                "height_cm"
            ),
            (
                f"ارتفاع بسته شماره "
                f"{index} مشخص نیست."
            ),
        )

        # Pricing واقعی Tipax قبلاً نشان داد
        # Weight بر حسب کیلوگرم ارسال می‌شود.
        weight_kg = (
            Decimal(
                str(
                    weight_grams
                )
            )
            / Decimal("1000")
        )

        package_value = (
            client.to_tipax_amount(
                declared_value_toman
            )
        )

        tipax_package = {
            "originId": int(
                origin_id
            ),

            "destination": dict(
                destination
            ),

            "receiver": dict(
                receiver
            ),

            "weight": float(
                weight_kg
            ),

            "packageValue": int(
                package_value
            ),

            "length": _to_float(
                length_cm,
                field_name="طول",
            ),

            "width": _to_float(
                width_cm,
                field_name="عرض",
            ),

            "height": _to_float(
                height_cm,
                field_name="ارتفاع",
            ),

            "packingId": int(
                packing_id
            ),

            "packageContentId": int(
                package_content_id
            ),

            "packType": int(
                pack_type
            ),

            "serviceId": int(
                service_id
            ),

            "enableLabelPrivacy": (
                enable_label_privacy
            ),

            "paymentType": int(
                payment_type
            ),

            "pickupType": int(
                pickup_type
            ),

            "distributionType": int(
                distribution_type
            ),
        }

        # توضیح مختصر محتویات بسته.
        items = (
            package.get(
                "items"
            )
            or []
        )

        item_names = [
            str(
                item.get(
                    "product_name"
                )
                or ""
            ).strip()
            for item in items
        ]

        item_names = [
            name
            for name in item_names
            if name
        ]

        if item_names:

            tipax_package[
                "description"
            ] = "، ".join(
                item_names
            )[:500]

        tipax_packages.append(
            tipax_package
        )

    # =====================================================
    # Root Payload
    # =====================================================

    payload = {
        "packages": (
            tipax_packages
        ),

        # برای ارتباط سفارش فروشگاه
        # با سفارش Tipax.
        "traceCode": (
            order.order_number
        ),
    }

    customer_substation_code = str(
        shipment_options.get(
            "customer_substation_code"
        )
        or ""
    ).strip()

    if customer_substation_code:

        payload[
            "customerSubstationCode"
        ] = customer_substation_code

    return payload


# =========================================================
# Response Parser
# =========================================================


def parse_tipax_order_response(
    response,
):
    if not isinstance(
        response,
        dict,
    ):

        raise TipaxShipmentError(
            "پاسخ ثبت سفارش Tipax معتبر نیست."
        )

    # Endpoint فعلی مستقیم OmOrderListDto
    # برمی‌گرداند؛ برای Robustness ساختار data
    # را هم پشتیبانی می‌کنیم.
    data = response

    if (
        isinstance(
            response.get("data"),
            dict,
        )
    ):

        data = response[
            "data"
        ]

    order_id = (
        data.get(
            "orderId"
        )
    )

    if not order_id:

        raise TipaxShipmentError(
            (
                "Tipax orderId در پاسخ "
                "ثبت مرسوله وجود ندارد."
            )
        )

    raw_tracking_codes = (
        data.get(
            "trackingCodes"
        )
        or []
    )

    tracking_codes = [
        str(code).strip()
        for code in raw_tracking_codes
        if str(code).strip()
    ]

    return (
        str(order_id).strip(),
        tracking_codes,
    )


# =========================================================
# Create Shipment
# =========================================================


def create_tipax_shipment(
    *,
    order,
):
    """
    ثبت واقعی Shipment در Tipax.

    اگر Shipment قبلاً با موفقیت ثبت شده باشد،
    دوباره درخواست Create به Tipax ارسال نمی‌شود.

    اگر تلاش قبلی ناموفق بوده باشد،
    همان Shipment محلی دوباره استفاده می‌شود.
    """

    order = (
        Order.objects
        .select_related(
            "shipping_method"
        )
        .get(
            pk=order.pk
        )
    )

    # =====================================================
    # Validation
    # =====================================================

    if (
        order.payment_status
        != Order.PaymentStatus.PAID
    ):

        raise TipaxShipmentError(
            (
                "فقط سفارش پرداخت‌شده "
                "قابل ثبت در Tipax است."
            )
        )

    if order.shipping_provider != "tipax":

        raise TipaxShipmentError(
            "Provider سفارش Tipax نیست."
        )

    # =====================================================
    # Existing Shipment
    # =====================================================

    shipment = (
        Shipment.objects
        .filter(
            order=order,
            provider="tipax",
        )
        .order_by(
            "-created_at"
        )
        .first()
    )

    # قبلاً با موفقیت در Tipax ثبت شده.
    if (
        shipment is not None
        and shipment.external_order_id
    ):

        return shipment

    # =====================================================
    # Build Payload
    # =====================================================

    client = TipaxClient()

    payload = (
        build_tipax_shipment_payload(
            order=order,
            client=client,
        )
    )

    # =====================================================
    # Create/Re-use local Shipment
    # =====================================================

    if shipment is None:

        shipment = (
            Shipment.objects.create(
                order=order,

                shipping_method=(
                    order.shipping_method
                ),

                provider="tipax",

                status=(
                    Shipment.Status.CREATED
                ),

                quoted_amount_toman=(
                    order.shipping_amount_toman
                ),

                request_payload=payload,
            )
        )

    else:

        shipment.shipping_method = (
            order.shipping_method
        )

        shipment.quoted_amount_toman = (
            order.shipping_amount_toman
        )

        shipment.request_payload = payload

        shipment.status = (
            Shipment.Status.CREATED
        )

        shipment.save(
            update_fields=[
                "shipping_method",
                "quoted_amount_toman",
                "request_payload",
                "status",
                "updated_at",
            ]
        )

    # =====================================================
    # Tipax Create Order
    # =====================================================

    try:

        response = (
            client
            .create_order_with_predefined_origin(
                payload
            )
        )

    except TipaxRequestError as exc:

        shipment.response_payload = {
            "error": str(exc),
        }

        shipment.save(
            update_fields=[
                "response_payload",
                "updated_at",
            ]
        )

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    # =====================================================
    # Parse Response
    # =====================================================

    (
        external_order_id,
        tracking_codes,
    ) = parse_tipax_order_response(
        response
    )

    # =====================================================
    # Save Successful Shipment
    # =====================================================

    shipment.external_order_id = (
        external_order_id
    )

    shipment.tracking_codes = (
        tracking_codes
    )

    shipment.primary_tracking_code = (
        tracking_codes[0]
        if tracking_codes
        else ""
    )

    shipment.response_payload = (
        response
    )

    shipment.status = (
        Shipment.Status.REGISTERED
    )

    shipment.save(
        update_fields=[
            "external_order_id",
            "tracking_codes",
            "primary_tracking_code",
            "response_payload",
            "status",
            "updated_at",
        ]
    )

    return shipment


# =========================================================
# Tipax Status Mapping
# =========================================================

TIPAX_STATUS_MAP = {

    # ثبت اولیه
    "59": Shipment.Status.REGISTERED,

    # در حال پردازش
    "58": Shipment.Status.PROCESSING,

    # در انتظار تایید
    "61": Shipment.Status.PROCESSING,

    # ثبت درخواست جمع‌آوری
    "29": Shipment.Status.WAITING_PICKUP,

    # در دست جمع‌آوری
    "30": Shipment.Status.WAITING_PICKUP,

    # جمع‌آوری شد
    "38": Shipment.Status.COLLECTED,

    # تحویل به مرکز پردازش مبدا
    "39": Shipment.Status.COLLECTED,

    # در مسیر
    "62": Shipment.Status.SHIPPED,

    # رسیدن به شهر مقصد
    "60": Shipment.Status.SHIPPED,

    # تحویل به گیرنده
    "50": Shipment.Status.DELIVERED,

    # عودت
    "51": Shipment.Status.RETURNED,

    # برگشت به گره قبلی
    "52": Shipment.Status.RETURNED,

    # مختومه عودتی
    "63": Shipment.Status.RETURNED,

    # ابطال
    "34": Shipment.Status.CANCELLED,

    # لغو
    "57": Shipment.Status.CANCELLED,
}

# =========================================================
# Tracking Helpers
# =========================================================


def _get_tracking_record(
    tracking,
    *,
    primary_tracking_code="",
):
    """
    رکورد اصلی Tracking را از Response تیپاکس
    پیدا می‌کند.
    """

    if not isinstance(
        tracking,
        list,
    ):

        raise TipaxShipmentError(
            "پاسخ Tracking تیپاکس معتبر نیست."
        )

    if not tracking:

        raise TipaxShipmentError(
            "Tipax هیچ Tracking Record برنگرداند."
        )

    primary_tracking_code = str(
        primary_tracking_code
        or ""
    ).strip()

    if primary_tracking_code:

        for record in tracking:

            if not isinstance(
                record,
                dict,
            ):
                continue

            tracking_code = str(
                record.get(
                    "trackingCode"
                )
                or ""
            ).strip()

            if (
                tracking_code
                == primary_tracking_code
            ):

                return record

    for record in tracking:

        if isinstance(
            record,
            dict,
        ):

            return record

    raise TipaxShipmentError(
        "Tracking Record معتبر پیدا نشد."
    )


# =========================================================
# Final Amount
# =========================================================


def _extract_tipax_final_amount(
    *,
    tracking_record,
    parcels,
    client,
):
    """
    مبلغ نهایی واقعی Tipax را ابتدا از Tracking
    و در صورت نبودن از Parcel استخراج می‌کند.
    """

    provider_amount = None

    # -----------------------------------------------------
    # Tracking -> priceDetail
    # -----------------------------------------------------

    price_detail = (
        tracking_record.get(
            "priceDetail"
        )
        or {}
    )

    if isinstance(
        price_detail,
        dict,
    ):

        provider_amount = (
            price_detail.get(
                "finalAmount"
            )
        )

    # -----------------------------------------------------
    # Parcels -> result[0] -> orderCost
    # -----------------------------------------------------

    if (
        provider_amount is None
        and isinstance(
            parcels,
            dict,
        )
    ):

        results = (
            parcels.get(
                "result"
            )
            or []
        )

        if (
            isinstance(
                results,
                list,
            )
            and results
            and isinstance(
                results[0],
                dict,
            )
        ):

            order_cost = (
                results[0].get(
                    "orderCost"
                )
                or {}
            )

            if isinstance(
                order_cost,
                dict,
            ):

                provider_amount = (
                    order_cost.get(
                        "finalAmount"
                    )
                )

    if provider_amount is None:

        return None

    return client.to_toman(
        provider_amount
    )


# =========================================================
# Sync Tipax Tracking
# =========================================================


@transaction.atomic
def sync_tipax_shipment_tracking(
    *,
    shipment,
):
    """
    آخرین وضعیت Shipment را از Tipax دریافت و
    Snapshot می‌کند.

    Statusهای ناشناخته:
        provider_status ذخیره می‌شود،
        ولی Shipment.status تغییر نمی‌کند.
    """

    shipment = (
        Shipment.objects
        .select_for_update()
        .select_related(
            "order",
        )
        .get(
            pk=shipment.pk
        )
    )

    # =====================================================
    # Validation
    # =====================================================

    if shipment.provider != "tipax":

        raise TipaxShipmentError(
            "Provider این Shipment تیپاکس نیست."
        )

    if not shipment.external_order_id:

        raise TipaxShipmentError(
            (
                "Tipax orderId برای این Shipment "
                "وجود ندارد."
            )
        )

    client = TipaxClient()

    # =====================================================
    # Main Tracking
    # =====================================================

    try:

        tracking = (
            client.track_by_order_id(
                shipment.external_order_id
            )
        )

    except TipaxRequestError as exc:

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    tracking_record = (
        _get_tracking_record(
            tracking,
            primary_tracking_code=(
                shipment
                .primary_tracking_code
            ),
        )
    )

    # =====================================================
    # Optional Brief Tracking
    # =====================================================

    brief = None
    brief_error = None

    if shipment.primary_tracking_code:

        try:

            brief = (
                client.brief_tracking(
                    shipment
                    .primary_tracking_code
                )
            )

        except TipaxRequestError as exc:

            # خطای Brief نباید Sync اصلی را خراب کند.
            brief_error = str(
                exc
            )

    # =====================================================
    # Optional Parcel Data
    # =====================================================

    parcels = None
    parcels_error = None

    try:

        parcels = (
            client.get_parcels_by_order_id(
                shipment.external_order_id
            )
        )

    except TipaxRequestError as exc:

        parcels_error = str(
            exc
        )

    # =====================================================
    # Provider Status
    # =====================================================

    raw_status_id = (
        tracking_record.get(
            "statusId"
        )
    )

    provider_status_id = str(
        raw_status_id
        if raw_status_id is not None
        else ""
    ).strip()

    provider_status_name = str(
        tracking_record.get(
            "status"
        )
        or ""
    ).strip()

    # =====================================================
    # Local Status Mapping
    # =====================================================

    mapped_status = (
        TIPAX_STATUS_MAP.get(
            provider_status_id
        )
    )

    # اگر Status را نمی‌شناسیم،
    # وضعیت داخلی قبلی را حفظ می‌کنیم.
    if (
            mapped_status is not None
            and _should_apply_shipment_status(
        current_status=shipment.status,
        new_status=mapped_status,
    )
    ):
        shipment.status = (
            mapped_status
        )

    # =====================================================
    # Final Amount
    # =====================================================

    final_amount_toman = (
        _extract_tipax_final_amount(
            tracking_record=(
                tracking_record
            ),
            parcels=parcels,
            client=client,
        )
    )

    if final_amount_toman is not None:

        shipment.final_amount_toman = (
            final_amount_toman
        )

    # =====================================================
    # Tracking Snapshot
    # =====================================================

    shipment.tracking_payload = {

        "synced_at": (
            timezone.now()
            .isoformat()
        ),

        "tracking": (
            tracking
        ),

        "brief_tracking": (
            brief
        ),

        "brief_tracking_error": (
            brief_error
        ),

        "parcels": (
            parcels
        ),

        "parcels_error": (
            parcels_error
        ),
    }

    shipment.provider_status_id = (
        provider_status_id
    )

    shipment.provider_status_name = (
        provider_status_name
    )

    # =====================================================
    # Cancel timestamp
    # =====================================================

    if (
        shipment.status
        == Shipment.Status.CANCELLED
        and shipment.cancelled_at is None
    ):

        shipment.cancelled_at = (
            timezone.now()
        )

    # =====================================================
    # Save
    # =====================================================

    shipment.save(
        update_fields=[
            "status",
            "provider_status_id",
            "provider_status_name",
            "final_amount_toman",
            "tracking_payload",
            "cancelled_at",
            "updated_at",
        ]
    )

    # =====================================================
    # Sync Order Status
    # =====================================================

    sync_order_from_shipment(
        shipment=shipment
    )

    return shipment



# =========================================================
# Sync Order From Shipment
# =========================================================


@transaction.atomic
def sync_order_from_shipment(
    *,
    shipment,
):
    """
    وضعیت Order را بر اساس Shipment فقط
    به سمت جلو حرکت می‌دهد.

    Returned/Cancelled عمداً اینجا Order را
    تغییر نمی‌دهند؛ چون منطق مالی و Stock
    جداگانه نیاز دارند.
    """

    # Local import برای جلوگیری از Circular Import.
    from orders.services import (
        mark_order_delivered,
        mark_order_packing,
        mark_order_shipped,
    )

    shipment = (
        Shipment.objects
        .select_related(
            "order"
        )
        .get(
            pk=shipment.pk
        )
    )

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=shipment.order_id
        )
    )

    # =====================================================
    # Payment Guard
    # =====================================================

    if (
        order.payment_status
        != Order.PaymentStatus.PAID
    ):

        return order

    # =====================================================
    # Terminal Orders
    # =====================================================

    if order.status in {
        Order.Status.CANCELLED,
        Order.Status.EXPIRED,
    }:

        return order

    # اگر قبلاً Delivered شده، عقب نمی‌رویم.
    if (
        order.status
        == Order.Status.DELIVERED
    ):

        return order

    # =====================================================
    # No Order Transition Yet
    # =====================================================

    if shipment.status in {
        Shipment.Status.CREATED,
        Shipment.Status.REGISTERED,
        Shipment.Status.PROCESSING,
        Shipment.Status.WAITING_PICKUP,
    }:

        return order

    # =====================================================
    # Returned / Cancelled
    # =====================================================

    if shipment.status in {
        Shipment.Status.RETURNED,
        Shipment.Status.CANCELLED,
    }:

        # این موارد بعداً توسط Workflow جداگانه
        # Refund / Stock / Cancellation مدیریت می‌شوند.
        return order

    # =====================================================
    # Collected / Shipped
    # =====================================================

    if shipment.status in {
        Shipment.Status.COLLECTED,
        Shipment.Status.SHIPPED,
    }:

        # اگر هنوز Processing است، مرحله Packing
        # را به شکل قانونی طی می‌کنیم.
        if (
            order.status
            == Order.Status.PROCESSING
        ):

            order = mark_order_packing(
                order
            )

        # بعد Shipment واقعاً از فروشگاه خارج شده.
        if (
            order.status
            == Order.Status.PACKING
        ):

            order = mark_order_shipped(
                order
            )

        return order

    # =====================================================
    # Delivered
    # =====================================================

    if (
        shipment.status
        == Shipment.Status.DELIVERED
    ):

        # اگر Tracking مستقیم از Processing
        # به Delivered پریده باشد، تمام Transitionهای
        # قانونی را به ترتیب اجرا می‌کنیم.

        if (
            order.status
            == Order.Status.PROCESSING
        ):

            order = mark_order_packing(
                order
            )

        if (
            order.status
            == Order.Status.PACKING
        ):

            order = mark_order_shipped(
                order
            )

        if (
            order.status
            == Order.Status.SHIPPED
        ):

            order = mark_order_delivered(
                order
            )

        return order

    return order

# =========================================================
# Shipment Status Progression
# =========================================================


def _should_apply_shipment_status(
    *,
    current_status,
    new_status,
):
    """
    اجازه نمی‌دهد Tracking قدیمی‌تر وضعیت Shipment
    را به عقب برگرداند.

    Terminal statusها:
        DELIVERED
        RETURNED
        CANCELLED
    """

    if not new_status:

        return False

    if current_status == new_status:

        return True

    terminal_statuses = {
        Shipment.Status.DELIVERED,
        Shipment.Status.RETURNED,
        Shipment.Status.CANCELLED,
    }

    # وضعیت Terminal قبلی را با اطلاعات قدیمی‌تر
    # دوباره تغییر نمی‌دهیم.
    if current_status in terminal_statuses:

        return False

    # Terminal جدید قابل اعمال است.
    if new_status in terminal_statuses:

        return True

    rank = {
        Shipment.Status.CREATED: 0,
        Shipment.Status.REGISTERED: 1,
        Shipment.Status.PROCESSING: 2,
        Shipment.Status.WAITING_PICKUP: 3,
        Shipment.Status.COLLECTED: 4,
        Shipment.Status.SHIPPED: 5,
    }

    current_rank = rank.get(
        current_status,
        -1,
    )

    new_rank = rank.get(
        new_status,
        -1,
    )

    return new_rank >= current_rank

# =========================================================
# Cancel Tipax Shipment
# =========================================================


def cancel_tipax_shipment(
    *,
    shipment,
):
    """
    کل Order مربوط به Shipment را در Tipax لغو می‌کند.

    این تابع Order فروشگاه را CANCELLED نمی‌کند.
    Order پرداخت‌شده توسط Cancellation Workflow
    و Refund Service مدیریت می‌شود.

    نکته حیاتی:
        اگر نتیجه Cancel به علت Network Error
        نامشخص شود، این وضعیت در tracking_payload
        ذخیره می‌شود تا Retry خودکار انجام نشود.
    """

    shipment = (
        Shipment.objects
        .select_related(
            "order",
        )
        .get(
            pk=shipment.pk
        )
    )

    # =====================================================
    # Validation
    # =====================================================

    if shipment.provider != "tipax":

        raise TipaxShipmentError(
            "Provider این Shipment تیپاکس نیست."
        )

    if not shipment.external_order_id:

        raise TipaxShipmentError(
            (
                "Tipax orderId برای این Shipment "
                "وجود ندارد."
            )
        )

    # =====================================================
    # Already Cancelled
    # =====================================================

    if (
        shipment.status
        == Shipment.Status.CANCELLED
    ):

        return shipment

    # =====================================================
    # Delivered
    # =====================================================

    if (
        shipment.status
        == Shipment.Status.DELIVERED
    ):

        raise TipaxShipmentError(
            "مرسوله تحویل‌شده قابل لغو نیست."
        )

    # =====================================================
    # Previous Unknown Cancellation
    # =====================================================

    tracking_payload = (
        shipment.tracking_payload
        or {}
    )

    cancellation_data = (
        tracking_payload.get(
            "cancellation"
        )
        or {}
    )

    if (
        cancellation_data.get(
            "result"
        )
        == "indeterminate"
    ):

        raise TipaxShipmentIndeterminateError(
            (
                "نتیجه تلاش قبلی برای لغو Shipment "
                "در Tipax نامشخص است. "
                "Retry خودکار مجاز نیست."
            )
        )

    client = TipaxClient()

    # =====================================================
    # Provider Cancellation
    # =====================================================

    try:

        response = client.cancel_order(
            shipment.external_order_id
        )

    # =====================================================
    # UNKNOWN RESULT
    # =====================================================

    except TipaxIndeterminateError as exc:

        with transaction.atomic():

            shipment = (
                Shipment.objects
                .select_for_update()
                .get(
                    pk=shipment.pk
                )
            )

            now = timezone.now()

            tracking_payload = dict(
                shipment.tracking_payload
                or {}
            )

            tracking_payload[
                "cancellation"
            ] = {
                "requested_at": (
                    now.isoformat()
                ),

                "result": (
                    "indeterminate"
                ),

                "scope": (
                    "order"
                ),

                "provider_order_id": (
                    shipment.external_order_id
                ),

                "error": (
                    str(exc)
                ),
            }

            shipment.tracking_payload = (
                tracking_payload
            )

            shipment.save(
                update_fields=[
                    "tracking_payload",
                    "updated_at",
                ]
            )

        raise TipaxShipmentIndeterminateError(
            (
                "نتیجه لغو Shipment در Tipax "
                "نامشخص است. "
                "Refund نباید خودکار ادامه پیدا کند."
            )
        ) from exc

    # =====================================================
    # DEFINITE FAILURE
    # =====================================================

    except TipaxRequestError as exc:

        raise TipaxShipmentError(
            str(exc)
        ) from exc

    # =====================================================
    # Business Error With HTTP 200
    # =====================================================

    if (
        isinstance(
            response,
            dict,
        )
        and
        response.get(
            "isSuccess"
        )
        is False
    ):

        raise TipaxShipmentError(
            str(
                response.get(
                    "message"
                )
                or
                (
                    "لغو Shipment در Tipax "
                    "ناموفق بود."
                )
            )
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    with transaction.atomic():

        shipment = (
            Shipment.objects
            .select_for_update()
            .get(
                pk=shipment.pk
            )
        )

        now = timezone.now()

        tracking_payload = dict(
            shipment.tracking_payload
            or {}
        )

        tracking_payload[
            "cancellation"
        ] = {
            "cancelled_at": (
                now.isoformat()
            ),

            "result": (
                "succeeded"
            ),

            "scope": (
                "order"
            ),

            "provider_order_id": (
                shipment.external_order_id
            ),

            "response": (
                response
            ),
        }

        shipment.status = (
            Shipment.Status.CANCELLED
        )

        shipment.cancelled_at = now

        shipment.tracking_payload = (
            tracking_payload
        )

        shipment.save(
            update_fields=[
                "status",
                "cancelled_at",
                "tracking_payload",
                "updated_at",
            ]
        )

    return shipment