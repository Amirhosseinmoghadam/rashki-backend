from django.core.management.base import (
    BaseCommand,
)

from django.utils import timezone

from orders.models import Order

from orders.services import (
    expire_unpaid_order,
)


# =========================================================
# Command
# =========================================================


class Command(BaseCommand):

    help = (
        "Expire unpaid orders whose payment "
        "deadline has passed and release their "
        "reserved stock."
    )

    # =====================================================
    # Handle
    # =====================================================

    def handle(
        self,
        *args,
        **options,
    ):

        now = timezone.now()

        # =================================================
        # Eligible Orders
        # =================================================
        #
        # فعلاً Orderهایی با PaymentStatus=PENDING
        # را Expire نمی‌کنیم.
        #
        # دلیل:
        # ممکن است درخواست Provider در جریان باشد
        # یا پرداخت انجام شده ولی Callback هنوز
        # به Backend نرسیده باشد.
        #
        # برای PENDING بعداً یک سیستم
        # Payment Reconciliation جدا می‌سازیم.
        # =================================================

        orders = (
            Order.objects
            .filter(

                status=(
                    Order.Status
                    .PENDING_PAYMENT
                ),

                expires_at__lte=now,

                payment_status__in=[
                    Order.PaymentStatus.UNPAID,
                    Order.PaymentStatus.FAILED,
                ],
            )
            .order_by(
                "id"
            )
        )

        # تعداد Candidateهای اولیه.
        candidate_count = (
            orders.count()
        )

        expired_count = 0
        skipped_count = 0
        error_count = 0

        # =================================================
        # Process Orders
        # =================================================

        for order in orders.iterator(
            chunk_size=100
        ):

            try:

                result = (
                    expire_unpaid_order(
                        order
                    )
                )

                # ممکن است بین Query اولیه و اجرای Service،
                # وضعیت Order توسط Request دیگری تغییر کرده باشد.
                if (
                    result.status
                    == Order.Status.EXPIRED
                ):

                    expired_count += 1

                else:

                    skipped_count += 1

            except Exception as exc:

                error_count += 1

                self.stderr.write(
                    self.style.ERROR(
                        (
                            "Failed to expire order "
                            f"{order.order_number}: "
                            f"{exc}"
                        )
                    )
                )

        # =================================================
        # Result
        # =================================================

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Expire unpaid orders completed. "
                    f"Candidates: {candidate_count}, "
                    f"Expired: {expired_count}, "
                    f"Skipped: {skipped_count}, "
                    f"Errors: {error_count}."
                )
            )
        )