import requests

from django.conf import settings

from .base import (
    BasePaymentProvider,
    PaymentProviderConfigurationError,
    PaymentProviderIndeterminateError,
    PaymentProviderRequestError,
    PaymentProviderVerificationError,
    PaymentStartResult,
    PaymentVerifyResult,
)


# =========================================================
# ZarinPal Provider
# =========================================================


class ZarinPalProvider(
    BasePaymentProvider
):

    key = "zarinpal"

    # =====================================================
    # Init
    # =====================================================

    def __init__(self):

        # -------------------------------------------------
        # Credentials
        # -------------------------------------------------

        self.merchant_id = getattr(
            settings,
            "ZARINPAL_MERCHANT_ID",
            "",
        )

        self.access_token = getattr(
            settings,
            "ZARINPAL_ACCESS_TOKEN",
            "",
        )

        self.terminal_id = getattr(
            settings,
            "ZARINPAL_TERMINAL_ID",
            "",
        )

        # -------------------------------------------------
        # Environment
        # -------------------------------------------------

        self.sandbox = getattr(
            settings,
            "ZARINPAL_SANDBOX",
            False,
        )

        # -------------------------------------------------
        # Currency
        # -------------------------------------------------

        self.provider_currency = getattr(
            settings,
            "ZARINPAL_PROVIDER_CURRENCY",
            "IRT",
        ).upper()

        # -------------------------------------------------
        # GraphQL
        # -------------------------------------------------
        #
        # Refund معمولی زرین‌پال و بعضی سرویس‌های
        # Dashboard از GraphQL استفاده می‌کنند.
        #
        # در حال حاضر Access Token برای پروژه
        # تنظیم نشده و این مسیر در تست Payment /
        # Verify / Reversal استفاده نمی‌شود.
        # -------------------------------------------------

        self.graphql_url = getattr(
            settings,
            "ZARINPAL_GRAPHQL_URL",
            (
                "https://next.zarinpal.com/"
                "api/v4/graphql/"
            ),
        )

        # =================================================
        # Sandbox / Production URLs
        # =================================================
        #
        # نکته امنیتی مهم:
        #
        # وقتی sandbox=True است، URLهای Payment
        # به صورت اجباری روی Sandbox قرار می‌گیرند.
        #
        # بنابراین حتی اگر اشتباهاً URLهای Live
        # داخل base.py یا .env وجود داشته باشند،
        # Sandbox نمی‌تواند به Live تبدیل شود.
        # =================================================

        if self.sandbox:

            self.request_url = (
                "https://sandbox.zarinpal.com/"
                "pg/v4/payment/request.json"
            )

            self.verify_url = (
                "https://sandbox.zarinpal.com/"
                "pg/v4/payment/verify.json"
            )

            self.reverse_url = (
                "https://sandbox.zarinpal.com/"
                "pg/v4/payment/reverse.json"
            )

            self.gateway_url = (
                "https://sandbox.zarinpal.com/"
                "pg/StartPay/"
            )

        else:

            self.request_url = (
                getattr(
                    settings,
                    "ZARINPAL_REQUEST_URL",
                    "",
                )
                or
                (
                    "https://api.zarinpal.com/"
                    "pg/v4/payment/request.json"
                )
            )

            self.verify_url = (
                getattr(
                    settings,
                    "ZARINPAL_VERIFY_URL",
                    "",
                )
                or
                (
                    "https://api.zarinpal.com/"
                    "pg/v4/payment/verify.json"
                )
            )

            self.reverse_url = (
                getattr(
                    settings,
                    "ZARINPAL_REVERSE_URL",
                    "",
                )
                or
                (
                    "https://payment.zarinpal.com/"
                    "pg/v4/payment/reverse.json"
                )
            )

            self.gateway_url = (
                getattr(
                    settings,
                    "ZARINPAL_GATEWAY_URL",
                    "",
                )
                or
                (
                    "https://www.zarinpal.com/"
                    "pg/StartPay/"
                )
            )

        # -------------------------------------------------
        # HTTP Timeout
        # -------------------------------------------------

        self.timeout = getattr(
            settings,
            "PAYMENT_HTTP_TIMEOUT_SECONDS",
            15,
        )

        # =================================================
        # Configuration Validation
        # =================================================

        if not self.merchant_id:

            raise PaymentProviderConfigurationError(
                (
                    "ZARINPAL_MERCHANT_ID "
                    "تنظیم نشده است."
                )
            )

        if self.provider_currency not in {
            "IRT",
            "IRR",
        }:

            raise PaymentProviderConfigurationError(
                (
                    "ZARINPAL_PROVIDER_CURRENCY "
                    "باید IRT یا IRR باشد."
                )
            )

    # =====================================================
    # Helpers
    # =====================================================

    def _safe_json(
        self,
        response,
    ):

        try:

            return response.json()

        except ValueError as exc:

            raise PaymentProviderRequestError(
                (
                    "پاسخ دریافتی از زرین‌پال "
                    "JSON معتبر نیست."
                )
            ) from exc

    # =====================================================
    # Start Payment
    # =====================================================

    def start_payment(
        self,
        *,
        attempt,
        callback_url,
    ):

        provider_amount = (
            self.convert_toman_to_provider_amount(
                attempt.amount_toman
            )
        )

        payload = {

            "merchant_id": (
                self.merchant_id
            ),

            "amount": (
                provider_amount
            ),

            "callback_url": (
                callback_url
            ),

            "description": (
                f"پرداخت سفارش "
                f"{attempt.order.order_number}"
            ),

            # واحد پول را صریح ارسال می‌کنیم.
            "currency": (
                self.provider_currency
            ),
        }

        # -------------------------------------------------
        # Optional Metadata
        # -------------------------------------------------

        phone_number = getattr(
            attempt.order.user,
            "phone_number",
            None,
        )

        if phone_number:

            payload["metadata"] = {
                "mobile": (
                    phone_number
                ),
            }

        # -------------------------------------------------
        # Provider Request
        # -------------------------------------------------

        try:

            response = requests.post(
                self.request_url,

                json=payload,

                timeout=self.timeout,

                headers={
                    "Content-Type": (
                        "application/json"
                    ),

                    "Accept": (
                        "application/json"
                    ),
                },
            )

        except requests.RequestException as exc:

            raise PaymentProviderRequestError(
                (
                    "ارتباط با زرین‌پال "
                    "امکان‌پذیر نبود."
                )
            ) from exc

        data = self._safe_json(
            response
        )

        response_data = (
            data.get("data")
            or {}
        )

        errors = (
            data.get("errors")
            or {}
        )

        code = response_data.get(
            "code"
        )

        # -------------------------------------------------
        # Error
        # -------------------------------------------------

        if (
            not response.ok
            or code != 100
        ):

            error_code = (
                errors.get("code")
                or code
                or response.status_code
            )

            error_message = (
                errors.get("message")
                or response_data.get(
                    "message"
                )
                or
                (
                    "درخواست پرداخت زرین‌پال "
                    "ناموفق بود."
                )
            )

            raise PaymentProviderRequestError(
                (
                    f"زرین‌پال: "
                    f"{error_message} "
                    f"(code={error_code})"
                )
            )

        # -------------------------------------------------
        # Authority
        # -------------------------------------------------

        authority = response_data.get(
            "authority"
        )

        if not authority:

            raise PaymentProviderRequestError(
                (
                    "زرین‌پال Authority "
                    "برنگرداند."
                )
            )

        # -------------------------------------------------
        # Safe Audit Data
        # -------------------------------------------------
        #
        # Merchant ID داخل Audit DB ذخیره نمی‌شود.
        # -------------------------------------------------

        safe_request = {

            "amount": (
                provider_amount
            ),

            "currency": (
                self.provider_currency
            ),

            "callback_url": (
                callback_url
            ),

            "description": (
                payload["description"]
            ),
        }

        safe_response = {

            "code": (
                code
            ),

            "authority": (
                authority
            ),

            "message": (
                response_data.get(
                    "message"
                )
            ),

            "fee_type": (
                response_data.get(
                    "fee_type"
                )
            ),

            "fee": (
                response_data.get(
                    "fee"
                )
            ),
        }

        return PaymentStartResult(

            gateway_url=(
                f"{self.gateway_url}"
                f"{authority}"
            ),

            provider_reference=(
                authority
            ),

            provider_amount=(
                provider_amount
            ),

            provider_currency=(
                self.provider_currency
            ),

            provider_adjustment_toman=0,

            request_payload=(
                safe_request
            ),

            response_payload=(
                safe_response
            ),
        )

    # =====================================================
    # Verify Payment
    # =====================================================

    def verify_payment(
        self,
        *,
        attempt,
        callback_data,
    ):

        callback_status = str(
            callback_data.get(
                "Status",
                "",
            )
        ).upper()

        authority = str(
            callback_data.get(
                "Authority",
                "",
            )
        ).strip()

        # -------------------------------------------------
        # Authority Validation
        # -------------------------------------------------

        if not authority:

            raise PaymentProviderVerificationError(
                (
                    "Authority در Callback "
                    "وجود ندارد."
                )
            )

        if (
            authority
            != attempt.provider_reference
        ):

            raise PaymentProviderVerificationError(
                (
                    "Authority با PaymentAttempt "
                    "تطابق ندارد."
                )
            )

        # -------------------------------------------------
        # User Cancelled / Failed
        # -------------------------------------------------

        if callback_status != "OK":

            return PaymentVerifyResult(

                success=False,

                failure_code=(
                    callback_status
                    or "CANCELLED"
                ),

                failure_message=(
                    "پرداخت توسط کاربر "
                    "لغو یا ناموفق شد."
                ),

                response_payload={

                    "callback_status": (
                        callback_status
                    ),

                    "authority": (
                        authority
                    ),
                },
            )

        # =================================================
        # Real Verify
        # =================================================

        payload = {

            "merchant_id": (
                self.merchant_id
            ),

            # دقیقاً همان مبلغی که هنگام Start
            # برای Provider ارسال شده بود.
            "amount": (
                attempt.provider_amount
            ),

            "authority": (
                authority
            ),

            "currency": (
                attempt.provider_currency
            ),
        }

        try:

            response = requests.post(
                self.verify_url,

                json=payload,

                timeout=self.timeout,

                headers={
                    "Content-Type": (
                        "application/json"
                    ),

                    "Accept": (
                        "application/json"
                    ),
                },
            )

        except requests.RequestException as exc:

            raise PaymentProviderVerificationError(
                (
                    "ارتباط با زرین‌پال "
                    "برای Verify امکان‌پذیر نبود."
                )
            ) from exc

        result = self._safe_json(
            response
        )

        data = (
            result.get("data")
            or {}
        )

        errors = (
            result.get("errors")
            or {}
        )

        code = data.get(
            "code"
        )

        # -------------------------------------------------
        # Successful Verification
        # -------------------------------------------------
        #
        # 100:
        # اولین Verify موفق.
        #
        # 101:
        # قبلاً Verify شده است.
        #
        # برای Idempotency هر دو را موفق
        # در نظر می‌گیریم.
        # -------------------------------------------------

        if code in {
            100,
            101,
        }:

            ref_id = data.get(
                "ref_id"
            )

            return PaymentVerifyResult(

                success=True,

                already_verified=(
                    code == 101
                ),

                provider_transaction_id=(
                    str(ref_id)
                    if ref_id is not None
                    else None
                ),

                response_payload={

                    "code": (
                        code
                    ),

                    "ref_id": (
                        ref_id
                    ),

                    "card_pan": (
                        data.get(
                            "card_pan"
                        )
                    ),

                    "fee_type": (
                        data.get(
                            "fee_type"
                        )
                    ),

                    "fee": (
                        data.get(
                            "fee"
                        )
                    ),
                },
            )

        # -------------------------------------------------
        # Verification Failed
        # -------------------------------------------------

        error_code = (
            errors.get("code")
            or code
            or response.status_code
        )

        error_message = (
            errors.get("message")
            or data.get(
                "message"
            )
            or
            (
                "Verify زرین‌پال "
                "ناموفق بود."
            )
        )

        return PaymentVerifyResult(

            success=False,

            failure_code=(
                str(
                    error_code
                )
            ),

            failure_message=(
                str(
                    error_message
                )
            ),

            response_payload={

                "code": (
                    code
                ),

                "message": (
                    data.get(
                        "message"
                    )
                ),
            },
        )

    # =====================================================
    # GraphQL
    # =====================================================

    def _graphql(
        self,
        *,
        query,
        variables=None,
    ):
        """
        ارتباط با GraphQL زرین‌پال.

        این API برای Refund و سرویس‌های Dashboard
        استفاده می‌شود و نیازمند Access Token است.
        """

        if not self.access_token:

            raise PaymentProviderConfigurationError(
                (
                    "ZARINPAL_ACCESS_TOKEN "
                    "تنظیم نشده است."
                )
            )

        payload = {

            "query": (
                query
            ),

            "variables": (
                variables
                or {}
            ),
        }

        try:

            response = requests.post(
                self.graphql_url,

                json=payload,

                timeout=self.timeout,

                headers={
                    "Content-Type": (
                        "application/json"
                    ),

                    "Accept": (
                        "application/json"
                    ),

                    "Authorization": (
                        f"Bearer "
                        f"{self.access_token}"
                    ),
                },
            )

        except requests.RequestException as exc:

            raise PaymentProviderRequestError(
                (
                    "ارتباط با GraphQL زرین‌پال "
                    "امکان‌پذیر نبود."
                )
            ) from exc

        data = self._safe_json(
            response
        )

        if not response.ok:

            raise PaymentProviderRequestError(
                (
                    "درخواست GraphQL زرین‌پال "
                    "ناموفق بود."
                )
            )

        errors = data.get(
            "errors"
        )

        if errors:

            message = (

                errors[0].get(
                    "message"
                )

                if (
                    isinstance(
                        errors,
                        list,
                    )
                    and errors
                    and isinstance(
                        errors[0],
                        dict,
                    )
                )

                else str(
                    errors
                )
            )

            raise PaymentProviderRequestError(
                (
                    "زرین‌پال GraphQL: "
                    f"{message}"
                )
            )

        return data

    # =====================================================
    # Refund
    # =====================================================

    def refund_payment(
        self,
        *,
        session_id,
        amount_toman,
        description="",
        reason="CUSTOMER_REQUEST",
        method=None,
    ):
        """
        Refund رسمی زرین‌پال با AddRefund.

        Refund با Reversal متفاوت است.

        Refund از session_id استفاده می‌کند و
        می‌تواند برای مبالغ جزئی نیز استفاده شود.
        """

        session_id = str(
            session_id
            or ""
        ).strip()

        if not session_id:

            raise PaymentProviderConfigurationError(
                (
                    "session_id تراکنش "
                    "زرین‌پال وجود ندارد."
                )
            )

        provider_amount = (
            self.convert_toman_to_provider_amount(
                amount_toman
            )
        )

        query = """
        mutation AddRefund(
            $session_id: ID!,
            $amount: BigInteger!,
            $description: String,
            $method: InstantPayoutActionTypeEnum,
            $reason: RefundReasonEnum
        ) {
            resource: AddRefund(
                session_id: $session_id,
                amount: $amount,
                description: $description,
                method: $method,
                reason: $reason
            ) {
                terminal_id
                id
                amount
                timeline {
                    refund_amount
                    refund_time
                    refund_status
                }
            }
        }
        """

        variables = {

            "session_id": (
                session_id
            ),

            "amount": (
                provider_amount
            ),

            "description": (
                description
                or None
            ),

            "method": (
                method
            ),

            "reason": (
                reason
                or None
            ),
        }

        response = self._graphql(
            query=query,
            variables=variables,
        )

        resource = (
            response
            .get(
                "data",
                {},
            )
            .get(
                "resource"
            )
        )

        if not resource:

            raise PaymentProviderRequestError(
                (
                    "زرین‌پال اطلاعات Refund "
                    "را برنگرداند."
                )
            )

        return {

            "provider_refund_id": (
                str(
                    resource.get(
                        "id"
                    )
                    or ""
                )
            ),

            "provider_amount": (
                resource.get(
                    "amount"
                )
                or provider_amount
            ),

            "provider_currency": (
                self.provider_currency
            ),

            "response_payload": (
                resource
            ),
        }

    # =====================================================
    # Reversal
    # =====================================================

    def reverse_payment(
        self,
        *,
        attempt,
    ):
        """
        Reversal کامل تراکنش زرین‌پال.

        Reversal با Authority انجام می‌شود.

        این عملیات برای Refund جزئی نیست.
        Refund جزئی از GraphQL AddRefund و
        session_id استفاده می‌کند.
        """

        authority = str(
            attempt.provider_reference
            or ""
        ).strip()

        if not authority:

            raise PaymentProviderConfigurationError(
                (
                    "Authority پرداخت زرین‌پال "
                    "برای Reversal وجود ندارد."
                )
            )

        payload = {

            "merchant_id": (
                self.merchant_id
            ),

            "authority": (
                authority
            ),
        }

        # -------------------------------------------------
        # Financial Write Request
        # -------------------------------------------------

        try:

            response = requests.post(
                self.reverse_url,

                json=payload,

                timeout=self.timeout,

                headers={
                    "Content-Type": (
                        "application/json"
                    ),

                    "Accept": (
                        "application/json"
                    ),
                },
            )

        except requests.RequestException as exc:

            # -------------------------------------------------
            # بسیار مهم:
            #
            # در یک عملیات مالی Write، Timeout یا Network Error
            # لزوماً به معنی شکست عملیات نیست.
            #
            # ممکن است:
            #
            # 1. Request اصلاً به Provider نرسیده باشد.
            #
            # یا:
            #
            # 2. Provider عملیات را انجام داده باشد اما
            #    Response به سرور ما نرسیده باشد.
            #
            # بنابراین Retry خودکار خطر Double Refund دارد.
            # -------------------------------------------------

            raise PaymentProviderIndeterminateError(
                (
                    "نتیجه Reversal زرین‌پال "
                    "به دلیل خطای ارتباطی نامشخص است "
                    "و نیاز به بررسی مالی دارد."
                )
            ) from exc

        result = self._safe_json(
            response
        )

        data = (
            result.get("data")
            or {}
        )

        errors = (
            result.get("errors")
            or {}
        )

        # -------------------------------------------------
        # Response Code
        # -------------------------------------------------
        #
        # برای تحمل اختلاف جزئی در Response Shape،
        # ابتدا data.code و سپس top-level code
        # بررسی می‌شود.
        # -------------------------------------------------

        code = (

            data.get(
                "code"
            )

            if isinstance(
                data,
                dict,
            )

            else None
        )

        if code is None:

            code = result.get(
                "code"
            )

        # -------------------------------------------------
        # Message
        # -------------------------------------------------

        message = (

            data.get(
                "message"
            )

            if isinstance(
                data,
                dict,
            )

            else None
        )

        if not message:

            message = result.get(
                "message"
            )

        # -------------------------------------------------
        # Reversal Failed
        # -------------------------------------------------

        if (
            not response.ok
            or code != 100
        ):

            error_code = (

                errors.get(
                    "code"
                )

                if isinstance(
                    errors,
                    dict,
                )

                else None
            )

            error_message = (

                errors.get(
                    "message"
                )

                if isinstance(
                    errors,
                    dict,
                )

                else None
            )

            raise PaymentProviderRequestError(
                (
                    "Reversal زرین‌پال ناموفق بود: "
                    f"{error_message or message or 'Unknown error'} "
                    f"(code="
                    f"{error_code or code or response.status_code}"
                    f")"
                )
            )

        # -------------------------------------------------
        # Success
        # -------------------------------------------------
        #
        # Authority دوباره داخل Audit ذخیره نمی‌شود،
        # چون از PaymentAttempt قابل دسترسی است.
        # -------------------------------------------------

        return {

            "success": True,

            "code": (
                code
            ),

            "message": (
                message
                or "Reversal successful"
            ),
        }