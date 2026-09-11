from rest_framework import serializers

from payments.models import (
    PaymentAttempt,
    PaymentRefund,
)


# =========================================================
# Start Payment
# =========================================================


class PaymentStartSerializer(
    serializers.Serializer
):

    # شماره Order موردنظر.
    order_number = serializers.CharField(
        max_length=50,
    )

    # Provider انتخابی.
    provider = serializers.ChoiceField(
        choices=(
            PaymentAttempt
            .Provider
            .choices
        )
    )


# =========================================================
# Payment Attempt
# =========================================================


class PaymentAttemptSerializer(
    serializers.ModelSerializer
):

    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    class Meta:

        model = PaymentAttempt

        fields = [
            "public_id",
            "order_number",
            "provider",
            "status",

            "amount_toman",
            "provider_amount",
            "provider_currency",
            "provider_adjustment_toman",

            "provider_reference",
            "provider_transaction_id",

            "gateway_url",

            "started_at",
            "expires_at",
            "verified_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# =========================================================
# Create Refund
# =========================================================


class PaymentRefundCreateSerializer(
    serializers.Serializer
):

    # Order موردنظر برای Refund.
    order_number = serializers.CharField(
        max_length=50,
    )

    # اگر ارسال نشود یا null باشد:
    # تمام مبلغ باقی‌مانده Refund می‌شود.
    amount_toman = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )

    reason = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )

    description = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default="",
    )


# =========================================================
# Refund Detail
# =========================================================


class PaymentRefundSerializer(
    serializers.ModelSerializer
):

    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    payment_public_id = serializers.UUIDField(
        source="payment_attempt.public_id",
        read_only=True,
    )

    class Meta:

        model = PaymentRefund

        fields = [
            "public_id",

            "order_number",
            "payment_public_id",

            "provider",
            "status",

            "amount_toman",
            "provider_amount",
            "provider_currency",

            "provider_session_id",
            "provider_refund_id",

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
        ]

        read_only_fields = fields