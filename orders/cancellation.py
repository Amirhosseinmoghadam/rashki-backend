from dataclasses import dataclass

from django.db import transaction

from orders.models import Order

from orders.services import (
    InvalidOrderTransitionError,
    cancel_unpaid_order,
)

from payments.models import (
    PaymentRefund,
)

from payments.services import (
    PaymentRefundValidationError,
    create_payment_refund,
    execute_payment_refund,
)

from shipping.models import (
    Shipment,
)

from shipping.shipments.tipax import (
    TipaxShipmentError,
    TipaxShipmentIndeterminateError,
    cancel_tipax_shipment,
)
from django.utils import timezone

# =========================================================
# Exceptions
# =========================================================


class OrderCancellationError(
    Exception
):
    """
    خطای قطعی Cancellation Workflow.
    """

    pass


class OrderCancellationReviewRequired(
    OrderCancellationError
):
    """
    نتیجه یکی از عملیات خارجی نامشخص است.

    در این وضعیت Retry خودکار نباید انجام شود
    و نیاز به Reconciliation / بررسی Provider داریم.
    """

    pass


# =========================================================
# Result
# =========================================================


@dataclass
class OrderCancellationResult:

    order: Order

    shipment: Shipment | None = None

    refund: PaymentRefund | None = None

    already_cancelled: bool = False


# =========================================================
# Helpers
# =========================================================


def _get_latest_shipment(
    *,
    order,
):

    return (
        Shipment.objects
        .filter(
            order=order
        )
        .order_by(
            "-created_at"
        )
        .first()
    )


def _get_latest_refund(
    *,
    order,
):

    return (
        PaymentRefund.objects
        .filter(
            order=order
        )
        .order_by(
            "-created_at"
        )
        .first()
    )


def _default_refund_idempotency_key(
    *,
    order,
):

    return (
        f"order-cancellation-"
        f"{order.id}-"
        f"full-refund-v1"
    )


# =========================================================
# Main Cancellation Workflow
# =========================================================


def cancel_order_with_refund(
    *,
    order,
    reason="order_cancellation",
    description="",
    refund_idempotency_key=None,
):
    """
    Cancellation Orchestrator اصلی.

    Workflow:

        Unpaid Order
            ↓
        cancel_unpaid_order()

    Paid Order
            ↓
        بررسی Shipment
            ↓
        Cancel Tipax
            ↓
        Create Refund
            ↓
        Execute Refund / Reversal
            ↓
        Refund Service:
            Order -> CANCELLED
            Payment -> REFUNDED
            Stock -> RESTORED

    این تابع عمداً خودش Stock یا Order Status را
    بعد از Refund تغییر نمی‌دهد.

    مسئول Finalization مالی و Stock:
        execute_payment_refund()
    """

    # =====================================================
    # Phase 1
    # Load / Validate Order
    # =====================================================

    with transaction.atomic():

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=order.pk
            )
        )

        # =================================================
        # Already Cancelled
        # =================================================

        if (
            order.status
            == Order.Status.CANCELLED
        ):

            return OrderCancellationResult(
                order=order,

                shipment=(
                    _get_latest_shipment(
                        order=order
                    )
                ),

                refund=(
                    _get_latest_refund(
                        order=order
                    )
                ),

                already_cancelled=True,
            )

        # =================================================
        # Delivered
        # =================================================

        if (
            order.status
            == Order.Status.DELIVERED
        ):

            raise OrderCancellationError(
                (
                    "سفارش تحویل‌شده از مسیر "
                    "Cancellation عادی قابل لغو نیست."
                )
            )

        # =================================================
        # Expired
        # =================================================

        if (
            order.status
            == Order.Status.EXPIRED
        ):

            raise OrderCancellationError(
                "سفارش منقضی‌شده قابل لغو نیست."
            )

        # =================================================
        # Payment result still unknown
        # =================================================

        if (
            order.payment_status
            == Order.PaymentStatus.PENDING
        ):

            raise OrderCancellationReviewRequired(
                (
                    "نتیجه پرداخت سفارش هنوز "
                    "قطعی نشده است. "
                    "قبل از Cancellation باید "
                    "Payment Reconciliation انجام شود."
                )
            )

        # =================================================
        # Unpaid / Failed
        # =================================================

        if (
            order.status
            == Order.Status.PENDING_PAYMENT
            and
            order.payment_status
            in {
                Order.PaymentStatus.UNPAID,
                Order.PaymentStatus.FAILED,
            }
        ):

            try:

                cancelled_order = (
                    cancel_unpaid_order(
                        order=order
                    )
                )

            except InvalidOrderTransitionError as exc:

                raise OrderCancellationError(
                    str(exc)
                ) from exc

            return OrderCancellationResult(
                order=cancelled_order
            )

        # =================================================
        # Already Refunded but Order inconsistent
        # =================================================

        if (
            order.payment_status
            == Order.PaymentStatus.REFUNDED
        ):

            raise OrderCancellationReviewRequired(
                (
                    "Payment سفارش Refund شده، "
                    "اما Order هنوز CANCELLED نیست. "
                    "نیاز به بررسی وضعیت داخلی دارد."
                )
            )

        # =================================================
        # Partial Refund
        # =================================================

        if (
            order.payment_status
            == Order.PaymentStatus.PARTIALLY_REFUNDED
        ):

            raise OrderCancellationReviewRequired(
                (
                    "این سفارش قبلاً Partial Refund "
                    "شده است. Cancellation کامل فعلاً "
                    "نیاز به بررسی دستی دارد."
                )
            )

        # =================================================
        # Paid Only
        # =================================================

        if (
            order.payment_status
            != Order.PaymentStatus.PAID
        ):

            raise OrderCancellationError(
                (
                    "وضعیت پرداخت سفارش "
                    "برای Cancellation پشتیبانی نمی‌شود."
                )
            )

        # =================================================
        # Shipping Progress Guard
        # =================================================

        if order.status in {
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        }:

            raise OrderCancellationError(
                (
                    "سفارش ارسال‌شده یا تحویل‌شده "
                    "از مسیر Cancellation عادی "
                    "قابل لغو نیست."
                )
            )

    # =====================================================
    # Phase 2
    # Shipment
    #
    # External network request outside DB transaction.
    # =====================================================

    shipment = (
        _get_latest_shipment(
            order=order
        )
    )

    if shipment is not None:

        # -------------------------------------------------
        # Only Tipax currently supported
        # -------------------------------------------------

        if (
            shipment.provider
            != "tipax"
        ):

            raise OrderCancellationError(
                (
                    "Cancellation این Shipping Provider "
                    "هنوز پیاده‌سازی نشده است."
                )
            )

        # -------------------------------------------------
        # Shipment already progressed too far
        # -------------------------------------------------

        if shipment.status in {
            Shipment.Status.COLLECTED,
            Shipment.Status.SHIPPED,
            Shipment.Status.DELIVERED,
            Shipment.Status.RETURNED,
        }:

            raise OrderCancellationError(
                (
                    "مرسوله از مرحله قابل لغو عادی "
                    "عبور کرده است."
                )
            )

        # -------------------------------------------------
        # External shipment exists
        # -------------------------------------------------

        if shipment.external_order_id:

            try:

                shipment = (
                    cancel_tipax_shipment(
                        shipment=shipment
                    )
                )

            except TipaxShipmentIndeterminateError as exc:

                raise OrderCancellationReviewRequired(
                    (
                        "نتیجه لغو مرسوله در Tipax "
                        "نامشخص است. "
                        "Refund انجام نشد."
                    )
                ) from exc

            except TipaxShipmentError as exc:

                raise OrderCancellationError(
                    (
                        "لغو مرسوله Tipax "
                        f"ناموفق بود: {exc}"
                    )
                ) from exc

        else:

            # Shipment فقط داخل سیستم ما ساخته شده
            # و هنوز چیزی در Tipax ثبت نشده است.
            with transaction.atomic():

                shipment = (
                    Shipment.objects
                    .select_for_update()
                    .get(
                        pk=shipment.pk
                    )
                )

                if (
                        shipment.status
                        != Shipment.Status.CANCELLED
                ):

                    shipment.status = (
                        Shipment.Status.CANCELLED
                    )

                    if shipment.cancelled_at is None:
                        shipment.cancelled_at = (
                            timezone.now()
                        )

                    shipment.save(
                        update_fields=[
                            "status",
                            "cancelled_at",
                            "updated_at",
                        ]
                    )

        # -------------------------------------------------
        # Local Shipment only
        # -------------------------------------------------
        #
        # external_order_id ندارد؛
        # پس چیزی در Provider برای Cancel وجود ندارد.
        # -------------------------------------------------

    # =====================================================
    # Phase 3
    # Refund
    # =====================================================

    if not refund_idempotency_key:

        refund_idempotency_key = (
            _default_refund_idempotency_key(
                order=order
            )
        )

    try:

        refund = (
            create_payment_refund(

                order=order,

                amount_toman=None,

                reason=reason,

                description=(
                    description
                ),

                idempotency_key=(
                    refund_idempotency_key
                ),
            )
        )

    except PaymentRefundValidationError as exc:

        raise OrderCancellationError(
            (
                "ساخت Refund برای Cancellation "
                f"ناموفق بود: {exc}"
            )
        ) from exc

    # =====================================================
    # Phase 4
    # Execute Refund
    # =====================================================

    try:

        refund = (
            execute_payment_refund(
                refund=refund
            )
        )

    except PaymentRefundValidationError as exc:

        refund.refresh_from_db()

        # -------------------------------------------------
        # Financial result unknown
        # -------------------------------------------------

        if (
            refund.status
            == PaymentRefund
            .Status
            .REQUIRES_REVIEW
        ):

            raise (
                OrderCancellationReviewRequired(
                    (
                        "نتیجه Refund/Reversal "
                        "نامشخص است. "
                        "Retry خودکار انجام نشود."
                    )
                )
            ) from exc

        # -------------------------------------------------
        # Still Pending
        # -------------------------------------------------

        if (
            refund.status
            == PaymentRefund.Status.PENDING
        ):

            raise (
                OrderCancellationReviewRequired(
                    (
                        "Refund در وضعیت PENDING "
                        "باقی مانده است. "
                        "قبل از Retry نیاز به "
                        "Reconciliation داریم."
                    )
                )
            ) from exc

        raise OrderCancellationError(
            (
                "اجرای Refund/Reversal "
                f"ناموفق بود: {exc}"
            )
        ) from exc

    # =====================================================
    # Phase 5
    # Final State
    # =====================================================

    order.refresh_from_db()

    if shipment is not None:

        shipment.refresh_from_db()

    refund.refresh_from_db()

    # execute_payment_refund مسئول این Finalization است.
    if (
        order.status
        != Order.Status.CANCELLED
        or
        order.payment_status
        != Order.PaymentStatus.REFUNDED
        or
        refund.status
        != PaymentRefund.Status.SUCCEEDED
    ):

        raise OrderCancellationReviewRequired(
            (
                "Provider Refund موفق گزارش شده، "
                "اما وضعیت نهایی داخلی با انتظار "
                "مطابقت ندارد."
            )
        )

    return OrderCancellationResult(
        order=order,
        shipment=shipment,
        refund=refund,
        already_cancelled=False,
    )