from abc import (
    ABC,
    abstractmethod,
)

from dataclasses import dataclass


# =========================================================
# Exceptions
# =========================================================


class PaymentProviderError(Exception):
    """
    خطای پایه برای تمام Providerهای پرداخت.
    """

    pass


class PaymentProviderConfigurationError(
    PaymentProviderError
):
    """
    تنظیمات Provider ناقص یا نامعتبر است.

    مثال:
        Merchant ID تنظیم نشده باشد.
        Currency پشتیبانی نشود.
    """

    pass


class PaymentProviderRequestError(
    PaymentProviderError
):
    """
    Provider پاسخ قطعی خطا داده است.

    یعنی نتیجه عملیات مشخص است و Provider
    درخواست را نپذیرفته یا رد کرده است.
    """

    pass


class PaymentProviderVerificationError(
    PaymentProviderError
):
    """
    خطای مربوط به Verify پرداخت.

    مثال:
        Authority نامعتبر باشد.
        Verify Provider ناموفق باشد.
    """

    pass


class PaymentProviderIndeterminateError(
    PaymentProviderError
):
    """
    نتیجه یک عملیات مالی Write نامشخص است.

    مثال:

        Backend درخواست Refund/Reversal را ارسال می‌کند،
        اما قبل از دریافت پاسخ Provider:

            - Connection Timeout
            - Read Timeout
            - قطع شبکه

        اتفاق می‌افتد.

    در چنین شرایطی ممکن است Provider عملیات مالی
    را انجام داده باشد ولی پاسخ به Backend نرسیده باشد.

    بنابراین:

        Retry خودکار ممنوع است.

    Caller باید عملیات را روی وضعیت
    REQUIRES_REVIEW قرار دهد و ابتدا وضعیت واقعی
    Provider را بررسی کند.

    هدف:
        جلوگیری از Double Refund / Double Reversal.
    """

    pass


# =========================================================
# Start Result
# =========================================================


@dataclass
class PaymentStartResult:

    # URL پرداخت.
    gateway_url: str

    # Authority / Invoice ID.
    provider_reference: str

    # مبلغ واقعی Provider.
    provider_amount: int

    # واحد Provider.
    provider_currency: str

    # Adjustment به تومان.
    provider_adjustment_toman: int = 0

    # Request امن برای Audit.
    request_payload: dict | None = None

    # Response امن برای Audit.
    response_payload: dict | None = None


# =========================================================
# Verify Result
# =========================================================


@dataclass
class PaymentVerifyResult:

    # آیا تراکنش واقعاً موفق است؟
    success: bool

    # آیا قبلاً Verify شده بوده؟
    already_verified: bool = False

    # ref_id یا Transaction ID.
    provider_transaction_id: str | None = None

    # پاسخ Sanitized.
    response_payload: dict | None = None

    # Error Code.
    failure_code: str | None = None

    # Error Message.
    failure_message: str | None = None


# =========================================================
# Base Provider
# =========================================================


class BasePaymentProvider(
    ABC
):

    key = None

    provider_currency = "IRT"

    # =====================================================
    # Currency
    # =====================================================

    def convert_toman_to_provider_amount(
        self,
        amount_toman,
    ):
        """
        مبلغ داخلی سیستم که همیشه تومان است را
        به واحد مالی Provider تبدیل می‌کند.

        مثال:

            IRT:
                1,000,000 Toman
                → 1,000,000

            IRR:
                1,000,000 Toman
                → 10,000,000 Rial
        """

        if self.provider_currency == "IRT":

            return int(
                amount_toman
            )

        if self.provider_currency == "IRR":

            return int(
                amount_toman
            ) * 10

        raise PaymentProviderConfigurationError(
            (
                "واحد پول Provider "
                f"{self.provider_currency} "
                "پشتیبانی نمی‌شود."
            )
        )

    # =====================================================
    # Start
    # =====================================================

    @abstractmethod
    def start_payment(
        self,
        *,
        attempt,
        callback_url,
    ) -> PaymentStartResult:
        """
        ساخت Payment در Provider.

        خروجی باید PaymentStartResult باشد.
        """

        raise NotImplementedError

    # =====================================================
    # Verify
    # =====================================================

    @abstractmethod
    def verify_payment(
        self,
        *,
        attempt,
        callback_data,
    ) -> PaymentVerifyResult:
        """
        Verify واقعی Payment در Provider.

        Callback به تنهایی قابل اعتماد نیست.
        """

        raise NotImplementedError