import uuid

from django.db import (
    IntegrityError,
    transaction,
)
from django.db.models import Sum
from django.utils import timezone

from orders.models import Order
from orders.services import (
    InvalidOrderTransitionError,
    _release_order_stock,
    expire_unpaid_order,
    mark_order_paid,
)

from .models import (
    PaymentAttempt,
    PaymentRefund,
)

from .providers.base import (
    PaymentProviderError,
    PaymentProviderIndeterminateError,
)

from .providers.registry import (
    get_payment_provider,
)

from .selectors import (
    get_payment_attempt_queryset,
)


# =========================================================
# Exceptions
# =========================================================


class PaymentError(Exception):
    """
    خطای پایه Payment.
    """

    pass


class PaymentValidationError(
    PaymentError
):
    """
    خطاهای مربوط به Validation یا وضعیت Payment.
    """

    pass


class PaymentNotFoundError(
    PaymentError
):
    """
    زمانی که PaymentAttempt موردنظر پیدا نشود.
    """

    pass


class PaymentRefundValidationError(
    PaymentValidationError
):
    """
    خطاهای Validation مربوط به Refund.
    """

    pass


# =========================================================
# Provider Money
# =========================================================


def get_initial_provider_money(
    *,
    provider,
    amount_toman,
):
    """
    مبلغ داخلی سیستم که همیشه Toman است را
    به مبلغ موردنیاز Provider تبدیل می‌کند.

    مثال:

    سیستم:
        1,000,000 Toman

    Provider با IRT:
        1,000,000

    Provider با IRR:
        10,000,000
    """

    try:

        provider_obj = (
            get_payment_provider(
                provider
            )
        )

        provider_amount = (
            provider_obj
            .convert_toman_to_provider_amount(
                amount_toman
            )
        )

    except PaymentProviderError as exc:

        raise PaymentValidationError(
            str(exc)
        ) from exc

    return (
        provider_amount,
        provider_obj.provider_currency,
    )


# =========================================================
# Set Order Payment Status
# =========================================================


def _set_order_payment_status(
    order,
    payment_status,
):
    """
    وضعیت Payment مربوط به Order را تغییر می‌دهد.

    نکته مهم:
    اگر Order قبلاً PAID شده باشد،
    هیچ Attempt ناموفق دیگری اجازه ندارد
    آن را دوباره FAILED یا PENDING کند.
    """

    if (
        order.payment_status
        == Order.PaymentStatus.PAID
    ):
        return

    order.payment_status = (
        payment_status
    )

    order.save(
        update_fields=[
            "payment_status",
            "updated_at",
        ]
    )


# =========================================================
# Start Payment
# =========================================================


def start_payment(
    *,
    user,
    order_number,
    provider_key,
    callback_url_builder,
    idempotency_key=None,
):
    """
    Payment جدید را برای یک Order شروع می‌کند.

    Workflow:

    1. Order Lock می‌شود.
    2. وضعیت Order بررسی می‌شود.
    3. PaymentAttempt ساخته می‌شود.
    4. Transaction دیتابیس Commit می‌شود.
    5. خارج از Transaction با Provider ارتباط برقرار می‌شود.
    6. نتیجه Provider در Attempt ذخیره می‌شود.

    callback_url_builder:
        Function است که public_id را می‌گیرد
        و Callback URL نهایی را می‌سازد.

    مثال:

        callback_url_builder(
            attempt.public_id
        )
    """

    # =====================================================
    # Phase 1
    #
    # DB Validation + Attempt Creation
    # =====================================================

    with transaction.atomic():

        # -------------------------------------------------
        # Lock Order
        # -------------------------------------------------

        order = (
            Order.objects
            .select_for_update()
            .filter(
                order_number=order_number,
                user=user,
            )
            .first()
        )

        if order is None:

            raise PaymentValidationError(
                "سفارش موردنظر یافت نشد."
            )

        # -------------------------------------------------
        # Already Paid
        # -------------------------------------------------

        if (
            order.payment_status
            == Order.PaymentStatus.PAID
        ):

            raise PaymentValidationError(
                "این سفارش قبلاً پرداخت شده است."
            )

        # -------------------------------------------------
        # Order Status
        # -------------------------------------------------

        if (
            order.status
            != Order.Status.PENDING_PAYMENT
        ):

            raise PaymentValidationError(
                "این سفارش در وضعیت قابل پرداخت نیست."
            )

        # -------------------------------------------------
        # Expired Order
        # -------------------------------------------------

        if (
            order.expires_at
            <= timezone.now()
        ):

            # اگر Payment در وضعیت PENDING باشد،
            # expire_unpaid_order خودش Order را
            # فعلاً Expire نمی‌کند.
            expire_unpaid_order(
                order
            )

            raise PaymentValidationError(
                "مهلت پرداخت این سفارش تمام شده است."
            )

        # -------------------------------------------------
        # Provider
        # -------------------------------------------------

        valid_providers = dict(
            PaymentAttempt.Provider.choices
        )

        if (
            provider_key
            not in valid_providers
        ):

            raise PaymentValidationError(
                "روش پرداخت معتبر نیست."
            )

        # -------------------------------------------------
        # Idempotency Key
        # -------------------------------------------------

        if idempotency_key:

            idempotency_key = (
                str(idempotency_key)
                .strip()
            )

            if not idempotency_key:

                raise PaymentValidationError(
                    "Idempotency-Key معتبر نیست."
                )

        else:

            idempotency_key = (
                uuid.uuid4().hex
            )

        # -------------------------------------------------
        # Existing Idempotent Request
        # -------------------------------------------------

        existing = (
            PaymentAttempt.objects
            .filter(
                idempotency_key=(
                    idempotency_key
                )
            )
            .select_related(
                "order",
                "order__user",
            )
            .first()
        )

        if existing is not None:

            # Key نباید برای Request دیگری استفاده شده باشد.
            if (
                existing.order_id
                != order.id
                or
                existing.provider
                != provider_key
            ):

                raise PaymentValidationError(
                    (
                        "این Idempotency-Key قبلاً "
                        "برای درخواست دیگری "
                        "استفاده شده است."
                    )
                )

            # همان Attempt قبلی برگردانده می‌شود.
            return existing

        # -------------------------------------------------
        # Reuse Existing Pending Attempt
        # -------------------------------------------------

        reusable = (
            PaymentAttempt.objects
            .filter(
                order=order,
                provider=provider_key,
                status=(
                    PaymentAttempt
                    .Status
                    .PENDING
                ),
                expires_at__gt=(
                    timezone.now()
                ),
            )
            .exclude(
                gateway_url=""
            )
            .order_by(
                "-created_at"
            )
            .first()
        )

        if reusable is not None:

            return reusable

        # -------------------------------------------------
        # Provider Amount
        # -------------------------------------------------

        (
            provider_amount,
            provider_currency,
        ) = get_initial_provider_money(
            provider=provider_key,
            amount_toman=(
                order.total_toman
            ),
        )

        # -------------------------------------------------
        # Create Attempt
        # -------------------------------------------------

        try:

            attempt = (
                PaymentAttempt.objects.create(

                    order=order,

                    provider=provider_key,

                    status=(
                        PaymentAttempt
                        .Status
                        .CREATED
                    ),

                    # مبلغ اصلی Order به تومان.
                    amount_toman=(
                        order.total_toman
                    ),

                    # مبلغی که Provider دریافت می‌کند.
                    provider_amount=(
                        provider_amount
                    ),

                    provider_currency=(
                        provider_currency
                    ),

                    # در شروع صفر است.
                    #
                    # TCart ممکن است بعداً این را تغییر دهد.
                    provider_adjustment_toman=0,

                    idempotency_key=(
                        idempotency_key
                    ),

                    # Attempt بیشتر از Order
                    # اجازه فعالیت ندارد.
                    expires_at=(
                        order.expires_at
                    ),
                )
            )

        except IntegrityError as exc:

            raise PaymentValidationError(
                "درخواست پرداخت تکراری است."
            ) from exc

        # -------------------------------------------------
        # Order → Payment Pending
        # -------------------------------------------------

        _set_order_payment_status(
            order,
            Order.PaymentStatus.PENDING,
        )

    # =====================================================
    # Transaction تا اینجا Commit شده است.
    #
    # از اینجا به بعد Network Request داریم.
    # نباید DB Lock را باز نگه داریم.
    # =====================================================


    # =====================================================
    # Build Callback URL
    # =====================================================

    try:

        callback_url = (
            callback_url_builder(
                attempt.public_id
            )
        )

    except Exception as exc:

        # اگر حتی Callback URL ساخته نشود،
        # Attempt را Fail می‌کنیم.
        with transaction.atomic():

            locked_attempt = (
                PaymentAttempt.objects
                .select_for_update()
                .select_related(
                    "order"
                )
                .get(
                    pk=attempt.pk
                )
            )

            locked_attempt.status = (
                PaymentAttempt.Status.FAILED
            )

            locked_attempt.failure_code = (
                "callback_url_error"
            )

            locked_attempt.failure_message = (
                "ساخت Callback URL پرداخت ناموفق بود."
            )

            locked_attempt.failed_at = (
                timezone.now()
            )

            locked_attempt.save(
                update_fields=[
                    "status",
                    "failure_code",
                    "failure_message",
                    "failed_at",
                    "updated_at",
                ]
            )

            _set_order_payment_status(
                locked_attempt.order,
                Order.PaymentStatus.FAILED,
            )

        raise PaymentValidationError(
            "ساخت Callback URL پرداخت ناموفق بود."
        ) from exc


    # =====================================================
    # Phase 2
    #
    # External Provider Request
    # =====================================================

    try:

        provider = (
            get_payment_provider(
                provider_key
            )
        )

        result = (
            provider.start_payment(
                attempt=attempt,
                callback_url=(
                    callback_url
                ),
            )
        )

    except PaymentProviderError as exc:

        # Provider Start Failed.
        with transaction.atomic():

            locked_attempt = (
                PaymentAttempt.objects
                .select_for_update()
                .select_related(
                    "order"
                )
                .get(
                    pk=attempt.pk
                )
            )

            # اگر به هر دلیلی Attempt در همین فاصله
            # موفق شده باشد، آن را Failed نمی‌کنیم.
            if (
                locked_attempt.status
                != PaymentAttempt
                .Status
                .SUCCEEDED
            ):

                locked_attempt.status = (
                    PaymentAttempt
                    .Status
                    .FAILED
                )

                locked_attempt.failure_message = (
                    str(exc)
                )

                locked_attempt.failed_at = (
                    timezone.now()
                )

                locked_attempt.save(
                    update_fields=[
                        "status",
                        "failure_message",
                        "failed_at",
                        "updated_at",
                    ]
                )

                _set_order_payment_status(
                    locked_attempt.order,
                    Order.PaymentStatus.FAILED,
                )

        raise PaymentValidationError(
            str(exc)
        ) from exc


    # =====================================================
    # Phase 3
    #
    # Save Provider Start Result
    # =====================================================

    with transaction.atomic():

        attempt = (
            PaymentAttempt.objects
            .select_for_update()
            .select_related(
                "order"
            )
            .get(
                pk=attempt.pk
            )
        )

        # اگر در فاصله Request،
        # Attempt از مسیر دیگری Success شده باشد
        # دوباره آن را PENDING نمی‌کنیم.
        if (
            attempt.status
            == PaymentAttempt
            .Status
            .SUCCEEDED
        ):

            return attempt

        attempt.provider_reference = (
            result.provider_reference
        )

        attempt.gateway_url = (
            result.gateway_url
        )

        attempt.provider_amount = (
            result.provider_amount
        )

        attempt.provider_currency = (
            result.provider_currency
        )

        attempt.provider_adjustment_toman = (
            result.provider_adjustment_toman
        )

        attempt.request_payload = (
            result.request_payload
            or {}
        )

        attempt.response_payload = (
            result.response_payload
            or {}
        )

        attempt.status = (
            PaymentAttempt.Status.PENDING
        )

        attempt.failure_code = ""
        attempt.failure_message = ""

        attempt.started_at = (
            timezone.now()
        )

        attempt.save(
            update_fields=[
                "provider_reference",
                "gateway_url",
                "provider_amount",
                "provider_currency",
                "provider_adjustment_toman",
                "request_payload",
                "response_payload",
                "status",
                "failure_code",
                "failure_message",
                "started_at",
                "updated_at",
            ]
        )

    return attempt


# =========================================================
# Process Payment Callback
# =========================================================


def process_payment_callback(
    *,
    public_id,
    provider_key,
    callback_data,
):
    """
    Callback یک Provider را پردازش می‌کند.

    نکته امنیتی:

    Callback به‌تنهایی قابل اعتماد نیست.

    Provider.verify_payment()
    باید تراکنش را واقعاً Verify کند.

    فقط پس از success=True:

        PaymentAttempt → SUCCEEDED
        Order.payment_status → PAID
        Order.status → PROCESSING
    """

    # =====================================================
    # Initial Lookup
    # =====================================================

    attempt = (
        get_payment_attempt_queryset()
        .filter(
            public_id=public_id,
            provider=provider_key,
        )
        .first()
    )

    if attempt is None:

        raise PaymentNotFoundError(
            "PaymentAttempt پیدا نشد."
        )

    # =====================================================
    # Safe Callback Audit
    # =====================================================

    safe_callback = {
        str(key): str(value)
        for key, value
        in callback_data.items()
    }

    # =====================================================
    # Already Successful
    # =====================================================

    if (
        attempt.status
        == PaymentAttempt
        .Status
        .SUCCEEDED
    ):

        # Callback تکراری است.
        return attempt


    # =====================================================
    # Provider
    # =====================================================

    try:

        provider = (
            get_payment_provider(
                provider_key
            )
        )

        # =================================================
        # External Verify
        # =================================================

        result = (
            provider.verify_payment(
                attempt=attempt,
                callback_data=(
                    callback_data
                ),
            )
        )

    except PaymentProviderError as exc:

        raise PaymentValidationError(
            str(exc)
        ) from exc


    # =====================================================
    # Finalize Transaction
    # =====================================================

    with transaction.atomic():

        # -------------------------------------------------
        # Lock Attempt
        # -------------------------------------------------

        attempt = (
            PaymentAttempt.objects
            .select_for_update()
            .select_related(
                "order"
            )
            .get(
                pk=attempt.pk
            )
        )

        # -------------------------------------------------
        # Duplicate Callback
        # -------------------------------------------------

        if (
            attempt.status
            == PaymentAttempt
            .Status
            .SUCCEEDED
        ):

            return attempt

        # -------------------------------------------------
        # Lock Order
        # -------------------------------------------------

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=attempt.order_id
            )
        )

        attempt.order = order

        # -------------------------------------------------
        # Save Callback Audit
        # -------------------------------------------------

        attempt.callback_payload = (
            safe_callback
        )

        attempt.response_payload = (
            result.response_payload
            or {}
        )


        # =================================================
        # SUCCESS
        # =================================================

        if result.success:

            # اگر Order قبلاً PAID شده باشد،
            # ممکن است Callback تکراری از Attempt دیگری
            # رسیده باشد.
            #
            # Provider Payment واقعی را Success اعلام کرده،
            # بنابراین نباید آن را Failed جعل کنیم.
            if (
                order.payment_status
                == Order.PaymentStatus.PAID
            ):

                successful_attempt = (
                    PaymentAttempt.objects
                    .filter(
                        order=order,
                        status=(
                            PaymentAttempt
                            .Status
                            .SUCCEEDED
                        ),
                    )
                    .exclude(
                        pk=attempt.pk
                    )
                    .first()
                )

                if (
                    successful_attempt
                    is not None
                ):

                    raise PaymentValidationError(
                        (
                            "این سفارش قبلاً با "
                            "یک PaymentAttempt دیگر "
                            "پرداخت شده است و این "
                            "تراکنش نیازمند بررسی "
                            "مالی است."
                        )
                    )

            # ---------------------------------------------
            # Order State Check
            # ---------------------------------------------

            if order.status in {
                Order.Status.CANCELLED,
                Order.Status.EXPIRED,
            }:

                # Provider Success است،
                # پس نباید Attempt را Failed کنیم.
                #
                # Transaction Local Rollback می‌شود
                # و نیاز به Reconciliation داریم.
                raise PaymentValidationError(
                    (
                        "پرداخت در Provider موفق است، "
                        "اما سفارش قبلاً لغو یا "
                        "منقضی شده و نیازمند بررسی "
                        "مالی است."
                    )
                )

            # ---------------------------------------------
            # Attempt Success
            # ---------------------------------------------

            attempt.status = (
                PaymentAttempt
                .Status
                .SUCCEEDED
            )

            attempt.provider_transaction_id = (
                result.provider_transaction_id
                or ""
            )

            attempt.failure_code = ""
            attempt.failure_message = ""

            attempt.verified_at = (
                timezone.now()
            )

            try:

                attempt.save(
                    update_fields=[
                        "status",
                        "provider_transaction_id",
                        "callback_payload",
                        "response_payload",
                        "failure_code",
                        "failure_message",
                        "verified_at",
                        "updated_at",
                    ]
                )

            except IntegrityError as exc:

                # UniqueConstraint:
                # فقط یک Payment موفق برای هر Order.
                raise PaymentValidationError(
                    (
                        "برای این سفارش قبلاً "
                        "یک پرداخت موفق ثبت شده است."
                    )
                ) from exc

            # ---------------------------------------------
            # Order Paid
            # ---------------------------------------------

            try:

                mark_order_paid(
                    order
                )

            except (
                InvalidOrderTransitionError
            ) as exc:

                # چون داخل transaction.atomic هستیم،
                # ذخیره SUCCEEDED هم Rollback می‌شود.
                raise PaymentValidationError(
                    (
                        "پرداخت در Provider موفق است "
                        "اما وضعیت سفارش اجازه ثبت "
                        "پرداخت را نمی‌دهد: "
                        f"{exc}"
                    )
                ) from exc

            return attempt


        # =================================================
        # FAILED / CANCELLED
        # =================================================

        callback_status = (
            str(
                callback_data.get(
                    "Status",
                    "",
                )
            )
            .strip()
            .upper()
        )

        if callback_status in {
            "NOK",
            "CANCEL",
            "CANCELLED",
        }:

            attempt.status = (
                PaymentAttempt
                .Status
                .CANCELLED
            )

        else:

            attempt.status = (
                PaymentAttempt
                .Status
                .FAILED
            )

        attempt.failure_code = (
            result.failure_code
            or ""
        )

        attempt.failure_message = (
            result.failure_message
            or
            "پرداخت ناموفق بود."
        )

        attempt.failed_at = (
            timezone.now()
        )

        attempt.save(
            update_fields=[
                "status",
                "callback_payload",
                "response_payload",
                "failure_code",
                "failure_message",
                "failed_at",
                "updated_at",
            ]
        )

        # Attempt ناموفق نباید Order پرداخت‌شده
        # را Downgrade کند.
        _set_order_payment_status(
            order,
            Order.PaymentStatus.FAILED,
        )

        return attempt


# =========================================================
# Create Payment Refund
# =========================================================


@transaction.atomic
def create_payment_refund(
    *,
    order,
    amount_toman=None,
    reason="",
    description="",
    idempotency_key=None,
):
    """
    یک درخواست Refund محلی ایجاد می‌کند.

    این تابع هنوز هیچ Request خارجی
    به Provider ارسال نمی‌کند.

    مسئولیت‌ها:

    - Lock کردن Order
    - پیدا کردن PaymentAttempt موفق
    - جلوگیری از Refund بیشتر از مبلغ پرداخت
    - جلوگیری از Double Refund
    - Idempotency
    - ساخت PaymentRefund با status=CREATED
    """

    # =====================================================
    # Lock Order
    # =====================================================

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    # =====================================================
    # Order Payment Status
    # =====================================================

    if (
        order.payment_status
        not in {
            Order.PaymentStatus.PAID,
            Order.PaymentStatus.PARTIALLY_REFUNDED,
        }
    ):

        raise PaymentRefundValidationError(
            "این سفارش در وضعیت قابل بازپرداخت نیست."
        )

    # =====================================================
    # Successful Payment
    # =====================================================

    payment_attempt = (
        PaymentAttempt.objects
        .select_for_update()
        .filter(
            order=order,
            status=(
                PaymentAttempt
                .Status
                .SUCCEEDED
            ),
        )
        .first()
    )

    if payment_attempt is None:

        raise PaymentRefundValidationError(
            (
                "برای این سفارش PaymentAttempt "
                "موفق پیدا نشد."
            )
        )

    # =====================================================
    # Idempotency Key
    # =====================================================

    if idempotency_key:

        idempotency_key = (
            str(idempotency_key)
            .strip()
        )

        if not idempotency_key:

            raise PaymentRefundValidationError(
                "Idempotency-Key معتبر نیست."
            )

        existing = (
            PaymentRefund.objects
            .filter(
                idempotency_key=(
                    idempotency_key
                )
            )
            .select_related(
                "order",
                "payment_attempt",
            )
            .first()
        )

        if existing is not None:

            if (
                existing.order_id
                != order.id
                or
                existing.payment_attempt_id
                != payment_attempt.id
            ):

                raise PaymentRefundValidationError(
                    (
                        "این Idempotency-Key قبلاً "
                        "برای Refund دیگری "
                        "استفاده شده است."
                    )
                )

            # اگر Amount صریح ارسال شده،
            # باید با Request قبلی یکی باشد.
            if (
                amount_toman is not None
                and int(amount_toman)
                != existing.amount_toman
            ):

                raise PaymentRefundValidationError(
                    (
                        "این Idempotency-Key قبلاً "
                        "با مبلغ دیگری استفاده شده است."
                    )
                )

            return existing

    else:

        idempotency_key = (
            uuid.uuid4().hex
        )

    # =====================================================
    # Amount already reserved/refunded
    # =====================================================

    blocking_statuses = {
        PaymentRefund.Status.CREATED,
        PaymentRefund.Status.PENDING,
        PaymentRefund.Status.SUCCEEDED,
        PaymentRefund.Status.REQUIRES_REVIEW,
    }

    aggregation = (
        PaymentRefund.objects
        .filter(
            payment_attempt=payment_attempt,
            status__in=blocking_statuses,
        )
        .aggregate(
            total=Sum(
                "amount_toman"
            )
        )
    )

    already_reserved_toman = (
        aggregation["total"]
        or 0
    )

    paid_amount_toman = (
        payment_attempt.amount_toman
    )

    remaining_toman = (
        paid_amount_toman
        - already_reserved_toman
    )

    if remaining_toman <= 0:

        raise PaymentRefundValidationError(
            (
                "تمام مبلغ این پرداخت قبلاً "
                "Refund شده یا برای Refund "
                "رزرو شده است."
            )
        )

    # =====================================================
    # Requested Amount
    # =====================================================

    if amount_toman is None:

        # None یعنی Refund تمام مبلغ باقی‌مانده.
        amount_toman = (
            remaining_toman
        )

    try:

        amount_toman = int(
            amount_toman
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise PaymentRefundValidationError(
            "مبلغ Refund معتبر نیست."
        ) from exc

    if amount_toman <= 0:

        raise PaymentRefundValidationError(
            "مبلغ Refund باید بیشتر از صفر باشد."
        )

    if amount_toman > remaining_toman:

        raise PaymentRefundValidationError(
            (
                "مبلغ Refund از مبلغ قابل "
                "بازپرداخت بیشتر است."
            )
        )

    # =====================================================
    # Business Data
    # =====================================================

    reason = str(
        reason
        or ""
    ).strip()

    description = str(
        description
        or ""
    ).strip()

    # =====================================================
    # Create Refund
    # =====================================================

    try:

        refund = (
            PaymentRefund.objects.create(

                order=order,

                payment_attempt=(
                    payment_attempt
                ),

                provider=(
                    payment_attempt.provider
                ),

                status=(
                    PaymentRefund
                    .Status
                    .CREATED
                ),

                amount_toman=(
                    amount_toman
                ),

                provider_currency=(
                    payment_attempt
                    .provider_currency
                    or ""
                ),

                idempotency_key=(
                    idempotency_key
                ),

                reason=reason,

                description=(
                    description
                ),
            )
        )

    except IntegrityError as exc:

        # احتمال Race روی Idempotency Key.
        existing = (
            PaymentRefund.objects
            .filter(
                idempotency_key=(
                    idempotency_key
                )
            )
            .first()
        )

        if (
            existing is not None
            and existing.order_id
            == order.id
            and existing.payment_attempt_id
            == payment_attempt.id
            and existing.amount_toman
            == amount_toman
        ):

            return existing

        raise PaymentRefundValidationError(
            "درخواست Refund تکراری است."
        ) from exc

    return refund

# =========================================================
# Execute Payment Refund
# =========================================================


def execute_payment_refund(
    *,
    refund,
):
    """
    Refund واقعی را در Provider اجرا می‌کند.

    نسخه فعلی:

    ZarinPal:
        فقط Full Refund از طریق Reversal.

    Partial Refund:
        بعداً از AddRefund + session_id
        پیاده‌سازی می‌شود.

    نکته حیاتی:
        Network Request خارج از DB Transaction
        اجرا می‌شود.
    """

    # =====================================================
    # Phase 1
    #
    # Validation + Mark Pending
    # =====================================================

    with transaction.atomic():

        refund = (
            PaymentRefund.objects
            .select_for_update()
            .select_related(
                "order",
                "payment_attempt",
            )
            .get(
                pk=refund.pk
            )
        )

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=refund.order_id
            )
        )

        payment_attempt = (
            PaymentAttempt.objects
            .select_for_update()
            .get(
                pk=refund.payment_attempt_id
            )
        )

        # -------------------------------------------------
        # Already Succeeded
        # -------------------------------------------------

        if (
            refund.status
            == PaymentRefund.Status.SUCCEEDED
        ):

            return refund

        # -------------------------------------------------
        # Unknown financial result
        # -------------------------------------------------

        if (
            refund.status
            == PaymentRefund
            .Status
            .REQUIRES_REVIEW
        ):

            raise PaymentRefundValidationError(
                (
                    "نتیجه این Refund قبلاً "
                    "نامشخص شده است و قبل از "
                    "هر Retry نیاز به بررسی "
                    "Provider دارد."
                )
            )

        # -------------------------------------------------
        # Already Pending
        # -------------------------------------------------

        if (
            refund.status
            == PaymentRefund.Status.PENDING
        ):

            raise PaymentRefundValidationError(
                "این Refund در حال پردازش است."
            )

        # -------------------------------------------------
        # Only CREATED
        # -------------------------------------------------

        if (
            refund.status
            != PaymentRefund.Status.CREATED
        ):

            raise PaymentRefundValidationError(
                "این Refund در وضعیت قابل اجرا نیست."
            )

        # -------------------------------------------------
        # Payment must be successful
        # -------------------------------------------------

        if (
            payment_attempt.status
            != PaymentAttempt.Status.SUCCEEDED
        ):

            raise PaymentRefundValidationError(
                "پرداخت اصلی موفق نیست."
            )

        # -------------------------------------------------
        # Order payment state
        # -------------------------------------------------

        if (
            order.payment_status
            not in {
                Order.PaymentStatus.PAID,
                Order.PaymentStatus.PARTIALLY_REFUNDED,
            }
        ):

            raise PaymentRefundValidationError(
                "وضعیت مالی Order اجازه Refund نمی‌دهد."
            )

        # =================================================
        # Provider
        # =================================================

        if (
            refund.provider
            != PaymentAttempt.Provider.ZARINPAL
        ):

            raise PaymentRefundValidationError(
                (
                    "Refund واقعی این Provider "
                    "هنوز پیاده‌سازی نشده است."
                )
            )

        # =================================================
        # Current ZarinPal Implementation = FULL ONLY
        # =================================================

        if (
            refund.amount_toman
            != payment_attempt.amount_toman
        ):

            raise PaymentRefundValidationError(
                (
                    "در نسخه فعلی زرین‌پال فقط "
                    "Full Refund از طریق Reversal "
                    "فعال است. Partial Refund بعداً "
                    "با session_id انجام می‌شود."
                )
            )

        # -------------------------------------------------
        # Authority
        # -------------------------------------------------

        if not (
            payment_attempt.provider_reference
            or ""
        ).strip():

            raise PaymentRefundValidationError(
                "Authority پرداخت زرین‌پال وجود ندارد."
            )

        # =================================================
        # Provider Object
        # =================================================

        provider = get_payment_provider(
            refund.provider
        )

        if not hasattr(
            provider,
            "reverse_payment",
        ):

            raise PaymentRefundValidationError(
                "Provider قابلیت Reversal ندارد."
            )

        # =================================================
        # Pending before external request
        # =================================================

        refund.status = (
            PaymentRefund.Status.PENDING
        )

        refund.requested_at = (
            timezone.now()
        )

        refund.request_payload = {
            "operation": "reversal",

            # Authority را عمداً داخل Audit دوباره
            # ذخیره نمی‌کنیم.
            "amount_toman": (
                refund.amount_toman
            ),

            "provider": (
                refund.provider
            ),
        }

        refund.failure_code = ""
        refund.failure_message = ""

        refund.save(
            update_fields=[
                "status",
                "requested_at",
                "request_payload",
                "failure_code",
                "failure_message",
                "updated_at",
            ]
        )

    # =====================================================
    # Phase 2
    #
    # External Financial Request
    #
    # IMPORTANT:
    # هیچ DB Lock اینجا باز نیست.
    # =====================================================

    try:

        result = provider.reverse_payment(
            attempt=payment_attempt
        )

    # =====================================================
    # Indeterminate Result
    # =====================================================

    except PaymentProviderIndeterminateError as exc:

        with transaction.atomic():

            refund = (
                PaymentRefund.objects
                .select_for_update()
                .get(
                    pk=refund.pk
                )
            )

            # اگر از مسیر دیگری Success شده باشد
            # Downgrade نمی‌کنیم.
            if (
                refund.status
                != PaymentRefund.Status.SUCCEEDED
            ):

                refund.status = (
                    PaymentRefund
                    .Status
                    .REQUIRES_REVIEW
                )

                refund.failure_code = (
                    "provider_result_unknown"
                )

                refund.failure_message = (
                    str(exc)
                )

                refund.save(
                    update_fields=[
                        "status",
                        "failure_code",
                        "failure_message",
                        "updated_at",
                    ]
                )

        raise PaymentRefundValidationError(
            (
                "نتیجه Refund نامشخص است. "
                "Retry خودکار انجام نشود."
            )
        ) from exc

    # =====================================================
    # Definite Provider Failure
    # =====================================================

    except PaymentProviderError as exc:

        with transaction.atomic():

            refund = (
                PaymentRefund.objects
                .select_for_update()
                .get(
                    pk=refund.pk
                )
            )

            if (
                refund.status
                != PaymentRefund.Status.SUCCEEDED
            ):

                refund.status = (
                    PaymentRefund.Status.FAILED
                )

                refund.failure_code = (
                    "provider_rejected"
                )

                refund.failure_message = (
                    str(exc)
                )

                refund.failed_at = (
                    timezone.now()
                )

                refund.save(
                    update_fields=[
                        "status",
                        "failure_code",
                        "failure_message",
                        "failed_at",
                        "updated_at",
                    ]
                )

        raise PaymentRefundValidationError(
            str(exc)
        ) from exc

    # =====================================================
    # Phase 3
    #
    # Provider SUCCESS
    # =====================================================

    with transaction.atomic():

        refund = (
            PaymentRefund.objects
            .select_for_update()
            .select_related(
                "payment_attempt",
            )
            .get(
                pk=refund.pk
            )
        )

        # Idempotency Guard
        if (
            refund.status
            == PaymentRefund.Status.SUCCEEDED
        ):

            return refund

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=refund.order_id
            )
        )

        payment_attempt = (
            PaymentAttempt.objects
            .select_for_update()
            .get(
                pk=refund.payment_attempt_id
            )
        )

        now = timezone.now()

        # =================================================
        # Refund Success
        # =================================================

        refund.status = (
            PaymentRefund.Status.SUCCEEDED
        )

        refund.provider_amount = (
            payment_attempt.provider_amount
        )

        refund.provider_currency = (
            payment_attempt.provider_currency
        )

        refund.response_payload = (
            result
            or {}
        )

        refund.failure_code = ""
        refund.failure_message = ""

        refund.completed_at = now

        refund.save(
            update_fields=[
                "status",
                "provider_amount",
                "provider_currency",
                "response_payload",
                "failure_code",
                "failure_message",
                "completed_at",
                "updated_at",
            ]
        )

        # =================================================
        # Order Financial State
        # =================================================

        order.payment_status = (
            Order.PaymentStatus.REFUNDED
        )

        # =================================================
        # Release Stock Exactly Once
        # =================================================

        _release_order_stock(
            order
        )

        # =================================================
        # Cancel Order
        # =================================================

        order.status = (
            Order.Status.CANCELLED
        )

        if order.cancelled_at is None:

            order.cancelled_at = now

        order.save(
            update_fields=[
                "payment_status",
                "status",
                "stock_released_at",
                "cancelled_at",
                "updated_at",
            ]
        )

        return refund