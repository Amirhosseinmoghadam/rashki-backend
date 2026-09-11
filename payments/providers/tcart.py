from django.conf import settings

from .base import (
    BasePaymentProvider,
    PaymentProviderConfigurationError,
    PaymentStartResult,
    PaymentVerifyResult,
)


# =========================================================
# TCart Provider
# =========================================================


class TCartProvider(
    BasePaymentProvider
):

    key = "tcart"

    # TCart طبق مدل فعلی خودش
    # مبلغ یکتا را به تومان نمایش می‌دهد.
    provider_currency = "IRT"

    def __init__(self):

        self.api_token = getattr(
            settings,
            "TCART_API_TOKEN",
            "",
        )

        self.webhook_secret = getattr(
            settings,
            "TCART_WEBHOOK_SECRET",
            "",
        )

        self.create_invoice_url = getattr(
            settings,
            "TCART_CREATE_INVOICE_URL",
            "",
        )

        self.invoice_status_url = getattr(
            settings,
            "TCART_INVOICE_STATUS_URL",
            "",
        )

    # =====================================================
    # Start
    # =====================================================

    def start_payment(
        self,
        *,
        attempt,
        callback_url,
    ) -> PaymentStartResult:

        # جزئیات Endpoint و Payload را
        # بدون مستندات رسمی حدس نمی‌زنیم.
        #
        # وقتی مستندات TCart را فرستادی،
        # فقط همین بخش تکمیل خواهد شد.
        raise PaymentProviderConfigurationError(
            (
                "TCart در معماری فعال است، "
                "اما API Contract دقیق ساخت Invoice "
                "هنوز پیکربندی نشده است."
            )
        )

    # =====================================================
    # Verify
    # =====================================================

    def verify_payment(
        self,
        *,
        attempt,
        callback_data,
    ) -> PaymentVerifyResult:

        # Callback TCart باید ابتدا با الگوریتم
        # و Canonicalization دقیق مستندات خودش
        # HMAC-SHA256 Verify شود.
        #
        # چون Header و Signed Payload دقیق را
        # از روی حدس نمی‌سازیم، بعد از دریافت
        # Docs همین بخش تکمیل می‌شود.
        raise PaymentProviderConfigurationError(
            (
                "Verify امن TCart نیازمند "
                "مستندات دقیق Webhook Signature است."
            )
        )