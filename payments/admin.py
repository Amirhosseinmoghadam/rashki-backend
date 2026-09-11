from django.contrib import admin

from .models import (
    PaymentAttempt,
    PaymentRefund,
)


# =========================================================
# Payment Attempt Admin
# =========================================================


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(
    admin.ModelAdmin
):

    list_display = (
        "public_id",
        "order",
        "provider",
        "status",
        "formatted_amount",
        "provider_amount_display",
        "provider_reference",
        "provider_transaction_id",
        "created_at",
    )

    list_filter = (
        "provider",
        "status",
        "provider_currency",
        "created_at",
    )

    search_fields = (
        "public_id",
        "order__order_number",
        "order__user__phone_number",
        "provider_reference",
        "provider_transaction_id",
        "provider_session_id",
        "idempotency_key",
    )

    list_select_related = (
        "order",
        "order__user",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    readonly_fields = (
        "public_id",

        "order",

        "provider",
        "status",

        "amount_toman",
        "provider_amount",
        "provider_currency",
        "provider_adjustment_toman",

        "provider_reference",
        "provider_transaction_id",
        "provider_session_id",

        "gateway_url",

        "idempotency_key",

        "request_payload",
        "response_payload",
        "callback_payload",

        "failure_code",
        "failure_message",

        "started_at",
        "expires_at",
        "verified_at",
        "failed_at",

        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "public_id",
                    "order",
                    "provider",
                    "status",
                ),
            },
        ),

        (
            "مبالغ",
            {
                "fields": (
                    "amount_toman",
                    "provider_amount",
                    "provider_currency",
                    "provider_adjustment_toman",
                ),
            },
        ),

        (
            "اطلاعات Provider",
            {
                "fields": (
                    "provider_reference",
                    "provider_transaction_id",
                    "provider_session_id",
                    "gateway_url",
                    "idempotency_key",
                ),
            },
        ),

        (
            "خطا",
            {
                "fields": (
                    "failure_code",
                    "failure_message",
                ),
            },
        ),

        (
            "Audit",
            {
                "fields": (
                    "request_payload",
                    "response_payload",
                    "callback_payload",
                ),

                "classes": (
                    "collapse",
                ),
            },
        ),

        (
            "زمان‌ها",
            {
                "fields": (
                    "started_at",
                    "expires_at",
                    "verified_at",
                    "failed_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def has_add_permission(
        self,
        request,
    ):

        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        # Audit مالی حذف نمی‌شود.
        return False

    @admin.display(
        description="مبلغ سفارش"
    )
    def formatted_amount(
        self,
        obj,
    ):

        return (
            f"{obj.amount_toman:,} تومان"
        )

    @admin.display(
        description="مبلغ Provider"
    )
    def provider_amount_display(
        self,
        obj,
    ):

        return (
            f"{obj.provider_amount:,} "
            f"{obj.provider_currency}"
        )


# =========================================================
# Payment Refund Admin
# =========================================================


@admin.register(PaymentRefund)
class PaymentRefundAdmin(
    admin.ModelAdmin
):
    """
    Refund یک Audit مالی است.

    بنابراین:

        Add از Admin ممنوع.
        Edit از Admin ممنوع.
        Delete ممنوع.

    اجرای Refund فقط از Service/API کنترل‌شده
    انجام می‌شود.
    """

    list_display = (
        "public_id",
        "order",
        "provider",
        "status",
        "formatted_amount",
        "provider_refund_id",
        "requested_at",
        "completed_at",
        "created_at",
    )

    list_filter = (
        "provider",
        "status",
        "provider_currency",
        "created_at",
        "requested_at",
        "completed_at",
    )

    search_fields = (
        "public_id",

        "order__order_number",
        "order__user__phone_number",

        "payment_attempt__public_id",

        "provider_session_id",
        "provider_refund_id",

        "idempotency_key",

        "failure_code",
        "failure_message",
    )

    list_select_related = (
        "order",
        "order__user",
        "payment_attempt",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    readonly_fields = (
        "public_id",

        "order",
        "payment_attempt",

        "provider",
        "status",

        "amount_toman",
        "provider_amount",
        "provider_currency",

        "provider_session_id",
        "provider_refund_id",

        "idempotency_key",

        "reason",
        "description",

        "request_payload",
        "response_payload",

        "failure_code",
        "failure_message",

        "requested_at",
        "completed_at",
        "failed_at",

        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "public_id",

                    "order",
                    "payment_attempt",

                    "provider",
                    "status",
                ),
            },
        ),

        (
            "مبلغ",
            {
                "fields": (
                    "amount_toman",
                    "provider_amount",
                    "provider_currency",
                ),
            },
        ),

        (
            "Provider",
            {
                "fields": (
                    "provider_session_id",
                    "provider_refund_id",
                    "idempotency_key",
                ),
            },
        ),

        (
            "دلیل Refund",
            {
                "fields": (
                    "reason",
                    "description",
                ),
            },
        ),

        (
            "خطا",
            {
                "fields": (
                    "failure_code",
                    "failure_message",
                ),
            },
        ),

        (
            "Audit",
            {
                "fields": (
                    "request_payload",
                    "response_payload",
                ),

                "classes": (
                    "collapse",
                ),
            },
        ),

        (
            "زمان‌ها",
            {
                "fields": (
                    "requested_at",
                    "completed_at",
                    "failed_at",

                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def has_add_permission(
        self,
        request,
    ):

        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        # رکورد مالی هرگز از Admin حذف نمی‌شود.
        return False

    @admin.display(
        description="مبلغ Refund"
    )
    def formatted_amount(
        self,
        obj,
    ):

        return (
            f"{obj.amount_toman:,} تومان"
        )