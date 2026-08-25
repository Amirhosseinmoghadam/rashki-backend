"""
سرویس ماژولار درگاه پرداخت زرین‌پال برای Django
================================================

این فایل هیچ وابستگی مستقیمی به Modelهای پروژه ندارد.

هدف:
    قرار دادن تمام ارتباطات با SDK زرین‌پال در یک محل واحد.

مزیت:
    Viewها، Modelها و سایر قسمت‌های پروژه مجبور نیستند مستقیماً
    با SDK زرین‌پال کار کنند.

مبتنی بر:
    zarinpal-py-sdk

مستندات مورد استفاده:
    - Payment Request
    - Generate Payment URL
    - Payment Verification
    - Transaction Inquiry
    - Unverified Transactions
    - Transaction Reverse
    - Refund
    - Transactions List
    - Fee Calculation
    - Wages / Split Settlement
"""


from __future__ import annotations

from typing import Any

from django.conf import settings

from zarinpal import ZarinPal



# ============================================================
# ثابت‌های عمومی زرین‌پال
# ============================================================

# طبق مستندات:
# code = 100
# یعنی عملیات موفق بوده است.
ZARINPAL_SUCCESS_CODE = 100


# طبق مستندات:
# code = 101
# یعنی تراکنش قبلاً Verify شده است.
ZARINPAL_ALREADY_VERIFIED_CODE = 101


# وضعیت بازگشتی کاربر از درگاه
ZARINPAL_STATUS_OK = "OK"
ZARINPAL_STATUS_NOK = "NOK"


# واحدهای پولی معرفی‌شده در مستندات
CURRENCY_IRR = "IRR"
CURRENCY_IRT = "IRT"


# ============================================================
# Exception اختصاصی
# ============================================================

class ZarinPalServiceError(Exception):
    """
    خطای عمومی سرویس زرین‌پال.

    به جای اینکه در تمام Viewهای پروژه Exceptionهای مختلف
    SDK را مدیریت کنیم، می‌توانیم خطاهای سرویس را از اینجا
    کنترل کنیم.
    """

    pass


# ============================================================
# کلاس اصلی سرویس
# ============================================================

class ZarinPalService:
    """
    کلاس اصلی ارتباط با زرین‌پال.

    تمام عملیات زرین‌پال از طریق متدهای این کلاس انجام می‌شود.

    مثال:

        zarinpal = ZarinPalService()

        result = zarinpal.create_payment(
            amount=100000,
            callback_url="https://example.com/payment/callback/",
            description="خرید محصول"
        )

    """

    def __init__(
            self,
            merchant_id: str | None = None,
    ) -> None:

        self.merchant_id = (
            merchant_id
            if merchant_id is not None
            else getattr(
                settings,
                "ZARINPAL_MERCHANT_ID",
                "",
            )
        )

        if not self.merchant_id:
            raise ZarinPalServiceError(
                "ZARINPAL_MERCHANT_ID تنظیم نشده است."
            )

        self.client = ZarinPal(
            self.merchant_id
        )

    # ========================================================
    # Payment Request
    # ========================================================

    def create_payment(
        self,
        amount: int,
        callback_url: str,
        description: str,
        *,
        mobile: str | None = None,
        email: str | None = None,
        referrer_id: str | None = None,
        currency: str | None = None,
        card_pan: str | list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        wages: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        ایجاد درخواست پرداخت.

        پارامترهای اصلی طبق مستندات:

            amount
            description
            callback_url

        پارامترهای اختیاری:

            mobile
            email
            referrer_id
            currency
            cardPan
            metadata
            wages

        خروجی:
            پاسخ خام SDK زرین‌پال.

        در صورت موفقیت معمولاً:

            response["data"]["code"] == 100

        و:

            response["data"]["authority"]

        دریافت می‌شود.
        """

        # ----------------------------------------------------
        # اعتبارسنجی مبلغ
        # ----------------------------------------------------

        if not isinstance(amount, int):
            raise ZarinPalServiceError(
                "amount باید از نوع integer باشد."
            )

        if amount <= 0:
            raise ZarinPalServiceError(
                "amount باید بزرگ‌تر از صفر باشد."
            )

        # ----------------------------------------------------
        # اعتبارسنجی توضیحات
        # ----------------------------------------------------

        if not description:
            raise ZarinPalServiceError(
                "description الزامی است."
            )

        # ----------------------------------------------------
        # اعتبارسنجی Callback
        # ----------------------------------------------------

        if not callback_url:
            raise ZarinPalServiceError(
                "callback_url الزامی است."
            )

        # ----------------------------------------------------
        # ساخت Payload
        # ----------------------------------------------------

        payload: dict[str, Any] = {
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
        }

        # ----------------------------------------------------
        # پارامترهای اختیاری
        # ----------------------------------------------------

        if mobile:
            payload["mobile"] = mobile

        if email:
            payload["email"] = email

        if referrer_id:
            payload["referrer_id"] = referrer_id

        if currency:
            self._validate_currency(currency)
            payload["currency"] = currency

        if card_pan:
            payload["cardPan"] = card_pan

        if metadata:
            payload["metadata"] = metadata

        if wages:
            payload["wages"] = wages

        # ----------------------------------------------------
        # ارسال درخواست به زرین‌پال
        # ----------------------------------------------------

        try:

            response = self.client.payments.create(payload)

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در ایجاد درخواست پرداخت زرین‌پال: {exc}"
            ) from exc

        # ----------------------------------------------------
        # بررسی پاسخ
        # ----------------------------------------------------

        return response

    # ========================================================
    # دریافت Authority
    # ========================================================

    @staticmethod
    def get_authority(
        response: dict[str, Any],
    ) -> str:
        """
        استخراج authority از پاسخ create_payment.

        ساختار مورد انتظار:

            {
                "data": {
                    "code": 100,
                    "authority": "..."
                }
            }
        """

        try:

            authority = response["data"]["authority"]

        except (KeyError, TypeError) as exc:

            raise ZarinPalServiceError(
                "authority در پاسخ زرین‌پال وجود ندارد."
            ) from exc

        if not authority:

            raise ZarinPalServiceError(
                "authority دریافتی خالی است."
            )

        return authority

    # ========================================================
    # دریافت URL پرداخت
    # ========================================================

    def get_payment_url(
        self,
        authority: str,
    ) -> str:
        """
        ساخت URL نهایی پرداخت از روی authority.

        طبق مستندات SDK:

            generate_payment_url(authority)

        """

        if not authority:
            raise ZarinPalServiceError(
                "authority الزامی است."
            )

        try:

            return self.client.payments.generate_payment_url(
                authority
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در ساخت URL پرداخت: {exc}"
            ) from exc

    # ========================================================
    # ایجاد پرداخت + گرفتن URL در یک متد
    # ========================================================

    def create_payment_and_get_url(
        self,
        amount: int,
        callback_url: str,
        description: str,
        *,
        mobile: str | None = None,
        email: str | None = None,
        referrer_id: str | None = None,
        currency: str | None = None,
        card_pan: str | list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        wages: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        یک متد convenience برای:

            1. ایجاد Payment
            2. دریافت authority
            3. ساخت payment URL

        خروجی نمونه:

            {
                "response": ...,
                "authority": "...",
                "payment_url": "..."
            }
        """

        response = self.create_payment(
            amount=amount,
            callback_url=callback_url,
            description=description,
            mobile=mobile,
            email=email,
            referrer_id=referrer_id,
            currency=currency,
            card_pan=card_pan,
            metadata=metadata,
            wages=wages,
        )

        authority = self.get_authority(response)

        payment_url = self.get_payment_url(authority)

        return {
            "response": response,
            "authority": authority,
            "payment_url": payment_url,
        }

    # ========================================================
    # Verify
    # ========================================================

    def verify_payment(
        self,
        authority: str,
        amount: int,
    ) -> dict[str, Any]:
        """
        تأیید پرداخت.

        بسیار مهم:

        amount نباید از QueryString یا اطلاعات قابل اعتماد
        نبودن سمت کاربر گرفته شود.

        مبلغ باید از دیتابیس خود پروژه استخراج شود.

        مثال:

            amount = payment.amount

            zarinpal.verify_payment(
                authority=payment.authority,
                amount=amount,
            )

        طبق مستندات:
            code == 100
                پرداخت موفق

            code == 101
                تراکنش قبلاً Verify شده است.
        """

        if not authority:
            raise ZarinPalServiceError(
                "authority الزامی است."
            )

        if not isinstance(amount, int):
            raise ZarinPalServiceError(
                "amount باید integer باشد."
            )

        if amount <= 0:
            raise ZarinPalServiceError(
                "amount باید بزرگ‌تر از صفر باشد."
            )

        try:

            response = self.client.verifications.verify(
                {
                    "amount": amount,
                    "authority": authority,
                }
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در Verify پرداخت: {exc}"
            ) from exc

        return response

    # ========================================================
    # بررسی موفق بودن Verify
    # ========================================================

    @staticmethod
    def is_verified(
        response: dict[str, Any],
    ) -> bool:
        """
        بررسی می‌کند که آیا پاسخ Verify موفق بوده است یا خیر.

        طبق مستندات:

            100 = موفق
            101 = قبلاً Verify شده

        بنابراین هر دو حالت را به عنوان تراکنش تأییدشده
        در نظر می‌گیریم.

        توجه:
        اینکه در پروژه شما code=101 باید چگونه مدیریت شود،
        وابسته به منطق Transaction/Payment شماست.
        """

        try:

            code = response["data"]["code"]

        except (KeyError, TypeError):

            return False

        return code in (
            ZARINPAL_SUCCESS_CODE,
            ZARINPAL_ALREADY_VERIFIED_CODE,
        )

    # ========================================================
    # استخراج Ref ID
    # ========================================================

    @staticmethod
    def get_ref_id(
        response: dict[str, Any],
    ) -> Any:
        """
        استخراج ref_id از پاسخ Verify.
        """

        try:

            return response["data"]["ref_id"]

        except (KeyError, TypeError):

            return None

    # ========================================================
    # Inquiry
    # ========================================================

    def inquire_payment(
        self,
        authority: str,
    ) -> dict[str, Any]:
        """
        استعلام یک تراکنش با استفاده از authority.

        طبق مستندات:

            zarinpal.inquiries.inquire({
                "authority": authority
            })
        """

        if not authority:
            raise ZarinPalServiceError(
                "authority الزامی است."
            )

        try:

            response = self.client.inquiries.inquire(
                {
                    "authority": authority
                }
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در Inquiry تراکنش: {exc}"
            ) from exc

        return response

    # ========================================================
    # Unverified Payments
    # ========================================================

    def get_unverified_payments(
        self,
    ) -> dict[str, Any]:
        """
        دریافت تراکنش‌های تأیید نشده.

        طبق مستندات:

            zarinpal.unverified.list()
        """

        try:

            return self.client.unverified.list()

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در دریافت تراکنش‌های تأیید نشده: {exc}"
            ) from exc

    # ========================================================
    # Reverse
    # ========================================================

    def reverse_payment(
        self,
        authority: str,
    ) -> dict[str, Any]:
        """
        Reverse کردن تراکنش.

        طبق مستندات:

        - برای تراکنش‌های موفق
        - حداکثر تا ۳۰ دقیقه بعد از پرداخت
        - بدون کارمزد

        ورودی:
            authority
        """

        if not authority:
            raise ZarinPalServiceError(
                "authority الزامی است."
            )

        try:

            response = self.client.reversals.reverse(
                {
                    "authority": authority
                }
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در Reverse تراکنش: {exc}"
            ) from exc

        return response

    # ========================================================
    # Refund
    # ========================================================

    def refund_payment(
        self,
        session_id: str,
        amount: int,
        description: str,
        method: str,
        reason: str,
    ) -> dict[str, Any]:
        """
        استرداد وجه.

        پارامترهای مستندات:

            session_id
            amount
            description
            method
            reason

        method:

            CARD
            PAYA

        """

        if not session_id:
            raise ZarinPalServiceError(
                "session_id الزامی است."
            )

        if not isinstance(amount, int):
            raise ZarinPalServiceError(
                "amount باید integer باشد."
            )

        if amount <= 0:
            raise ZarinPalServiceError(
                "amount باید بزرگ‌تر از صفر باشد."
            )

        if not description:
            raise ZarinPalServiceError(
                "description الزامی است."
            )

        if method not in ("CARD", "PAYA"):
            raise ZarinPalServiceError(
                "method باید CARD یا PAYA باشد."
            )

        if not reason:
            raise ZarinPalServiceError(
                "reason الزامی است."
            )

        try:

            response = self.client.refunds.create(
                {
                    "session_id": session_id,
                    "amount": amount,
                    "description": description,
                    "method": method,
                    "reason": reason,
                }
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در Refund تراکنش: {exc}"
            ) from exc

        return response

    # ========================================================
    # Transactions List
    # ========================================================

    def list_transactions(
        self,
        terminal_id: str,
        *,
        filter_status: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        دریافت لیست تراکنش‌ها.

        پارامترها طبق مستندات:

            terminal_id
            filter
            offset
            limit

        وضعیت‌های filter معرفی‌شده:

            PAID
            VERIFIED
            TRASH
            ACTIVE
            REFUNDED
        """

        if not terminal_id:
            raise ZarinPalServiceError(
                "terminal_id الزامی است."
            )

        payload: dict[str, Any] = {
            "terminal_id": terminal_id
        }

        if filter_status:

            allowed_filters = {
                "PAID",
                "VERIFIED",
                "TRASH",
                "ACTIVE",
                "REFUNDED",
            }

            if filter_status not in allowed_filters:
                raise ZarinPalServiceError(
                    "filter_status نامعتبر است."
                )

            payload["filter"] = filter_status

        if offset is not None:

            if offset < 0:
                raise ZarinPalServiceError(
                    "offset نمی‌تواند منفی باشد."
                )

            payload["offset"] = offset

        if limit is not None:

            if limit <= 0:
                raise ZarinPalServiceError(
                    "limit باید بزرگ‌تر از صفر باشد."
                )

            payload["limit"] = limit

        try:

            return self.client.transactions.list(
                payload
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در دریافت لیست تراکنش‌ها: {exc}"
            ) from exc

    # ========================================================
    # Fee Calculation
    # ========================================================

    def calculate_fee(
        self,
        amount: int,
        *,
        currency: str = CURRENCY_IRR,
    ) -> dict[str, Any]:
        """
        محاسبه کارمزد تراکنش.

        طبق مستندات:

            amount
            currency

        currency:

            IRR
            IRT
        """

        if not isinstance(amount, int):
            raise ZarinPalServiceError(
                "amount باید integer باشد."
            )

        if amount <= 1000:
            raise ZarinPalServiceError(
                "طبق مستندات amount باید بیشتر از 1000 ریال باشد."
            )

        self._validate_currency(currency)

        try:

            return self.client.fee.calculate(
                {
                    "amount": amount,
                    "currency": currency,
                }
            )

        except Exception as exc:

            raise ZarinPalServiceError(
                f"خطا در محاسبه کارمزد: {exc}"
            ) from exc

    # ========================================================
    # Validation Currency
    # ========================================================

    @staticmethod
    def _validate_currency(
        currency: str,
    ) -> None:
        """
        بررسی واحد پولی.

        طبق مستندات:

            IRR = ریال
            IRT = تومان
        """

        if currency not in (
            CURRENCY_IRR,
            CURRENCY_IRT,
        ):

            raise ZarinPalServiceError(
                "currency باید IRR یا IRT باشد."
            )

    # ========================================================
    # بررسی Status بازگشتی
    # ========================================================

    @staticmethod
    def is_callback_success(
        status: str | None,
    ) -> bool:
        """
        بررسی Status بازگشتی از زرین‌پال.

        طبق مستندات:

            OK  = پرداخت برای Verify آماده است
            NOK = پرداخت ناموفق/لغو شده

        """

        return status == ZARINPAL_STATUS_OK

    # ========================================================
    # دریافت اطلاعات اصلی Verify
    # ========================================================

    @staticmethod
    def extract_verify_data(
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """
        استخراج اطلاعات مهم از پاسخ Verify.

        خروجی:

            {
                "code": ...,
                "message": ...,
                "ref_id": ...,
                "card_pan": ...,
                "card_hash": ...,
                "fee_type": ...,
                "fee": ...
            }

        """

        data = response.get("data", {})

        return {
            "code": data.get("code"),
            "message": data.get("message"),
            "ref_id": data.get("ref_id"),
            "card_pan": data.get("card_pan"),
            "card_hash": data.get("card_hash"),
            "fee_type": data.get("fee_type"),
            "fee": data.get("fee"),
        }