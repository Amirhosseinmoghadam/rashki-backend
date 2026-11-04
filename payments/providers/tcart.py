"""TCart Partner API (https://tcartt.com/docs), amounts are in toman."""
import hashlib
import hmac
import json
from datetime import datetime
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.utils import timezone

from .base import (
    BasePaymentProvider, PaymentStartResult, PaymentVerifyResult,
    PaymentProviderConfigurationError, PaymentProviderRequestError,
    PaymentProviderIndeterminateError, PaymentProviderVerificationError,
)


class TCartProvider(BasePaymentProvider):
    key = "tcart"
    provider_currency = "IRT"
    BASE = "https://tcartt.com"

    def __init__(self):
        self.api_token = getattr(settings, "TCART_API_TOKEN", "")
        self.callback_secret = getattr(settings, "TCART_CALLBACK_SECRET", "")
        self.create_invoice_url = getattr(settings, "TCART_CREATE_INVOICE_URL", "") or self.BASE + "/api/v1/invoices"
        self.invoice_status_url = getattr(settings, "TCART_INVOICE_STATUS_URL", "") or self.BASE + "/api/v1/invoices/{invoice_id}"
        self.timeout = getattr(settings, "PAYMENT_HTTP_TIMEOUT_SECONDS", 15)

    def _ensure_config(self):
        if not self.api_token:
            raise PaymentProviderConfigurationError("TCART_API_TOKEN تنظیم نشده است")
        # Never send secrets to arbitrary URLs; fixed host required in production.
        for endpoint in (self.create_invoice_url, self.invoice_status_url):
            parsed = urlsplit(endpoint)
            if parsed.scheme != "https" or parsed.netloc != "tcartt.com":
                raise PaymentProviderConfigurationError("نشانی API تیکارت باید HTTPS و دامنه tcartt.com باشد")

    def _call(self, method, url, *, payload=None, is_write=False):
        self._ensure_config()
        try:
            response = requests.request(
                method, url, headers={"Authorization": f"Bearer {self.api_token}", "Accept": "application/json"},
                json=payload, timeout=self.timeout, allow_redirects=False,
            )
        except requests.RequestException as exc:
            error = PaymentProviderIndeterminateError if is_write else PaymentProviderVerificationError
            raise error("ارتباط با TCart نامشخص یا قطع شد؛ وضعیت پرداخت را قبل از تلاش مجدد بررسی کنید") from exc
        if response.status_code in (301, 302, 303, 307, 308):
            raise PaymentProviderRequestError("ریدایرکت غیرمنتظره در API تیکارت")
        try:
            body = response.json()
        except ValueError as exc:
            raise PaymentProviderVerificationError("پاسخ JSON معتبر از تیکارت دریافت نشد") from exc
        if not isinstance(body, dict):
            raise PaymentProviderVerificationError("فرمت پاسخ TCart نامعتبر است")
        if response.status_code >= 500:
            raise PaymentProviderIndeterminateError("خطای سرویس TCart؛ وضعیت پرداخت نامشخص است")
        if not response.ok or body.get("ok") is False:
            err = str(body.get("error", "provider_error"))[:200]
            raise PaymentProviderRequestError(f"TCart HTTP {response.status_code}: {err}")
        return body

    @staticmethod
    def _positive_int(value, name):
        if isinstance(value, bool):
            raise PaymentProviderVerificationError(f"{name} نامعتبر است")
        try:
            result = int(value)
        except (TypeError, ValueError) as exc:
            raise PaymentProviderVerificationError(f"{name} نامعتبر است") from exc
        if result <= 0:
            raise PaymentProviderVerificationError(f"{name} باید مثبت باشد")
        return result

    @staticmethod
    def verify_callback_signature(payload, header, secret):
        """TCart documentation: HMAC-SHA256 of JSON with sorted keys."""
        if not secret or not isinstance(payload, dict) or not isinstance(header, str):
            return False
        supplied = header.strip()
        if not supplied.startswith("sha256="):
            return False
        signature = supplied[7:]
        if len(signature) != 64 or any(x not in "0123456789abcdefABCDEF" for x in signature):
            return False
        # Published docs specify sort_keys, but not JSON separators; support both
        # conventional Python serialization and compact JSON, never raw body.
        representations = (
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
            json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
            json.dumps(payload, sort_keys=True),
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
        )
        return any(hmac.compare_digest(
            hmac.new(secret.encode(), content.encode("utf-8"), hashlib.sha256).hexdigest(), signature.lower()
        ) for content in representations)

    def start_payment(self, *, attempt, callback_url) -> PaymentStartResult:
        base = self._positive_int(attempt.amount_toman, "amount_toman")
        if base < 1000:
            raise PaymentProviderRequestError("حداقل مبلغ فاکتور TCart برابر ۱۰۰۰ تومان است")
        # Invoice expiry must never outlive the local order's expiry.
        seconds = (attempt.expires_at - timezone.now()).total_seconds()
        if seconds < 60:
            raise PaymentProviderRequestError("مهلت سفارش برای ایجاد فاکتور کافی نیست")
        expires_minutes = min(max(1, int(seconds // 60)), 60)
        order_no = str(attempt.order.order_number)
        payload = {
            "amount_toman": base,
            "title": f"سفارش {order_no}",
            "external_order_id": order_no,
            "buyer_ref": str(attempt.order.user_id),
            "return_url": getattr(settings, "TCART_RETURN_URL", "") or getattr(settings, "PAYMENT_SUCCESS_REDIRECT_URL", ""),
            "callback_url": callback_url,
            "expires_minutes": expires_minutes,
        }
        if not payload["return_url"].startswith("https://") or not callback_url.startswith("https://"):
            raise PaymentProviderConfigurationError("برای TCart لینک‌های عمومی HTTPS return_url و callback_url لازم هستند")
        body = self._call("POST", self.create_invoice_url, payload=payload, is_write=True)
        if body.get("ok") is not True or str(body.get("status")) != "pending":
            raise PaymentProviderVerificationError("ساخت فاکتور TCart پاسخ تأییدشده pending برنگرداند")
        invoice_id = self._positive_int(body.get("invoice_id"), "invoice_id")
        unique = self._positive_int(body.get("unique_amount_toman"), "unique_amount_toman")
        if self._positive_int(body.get("base_price_toman"), "base_price_toman") != base or unique < base:
            raise PaymentProviderVerificationError("مبلغ فاکتور ساخته‌شده با سفارش تطابق ندارد")
        if str(body.get("external_order_id")) != order_no:
            raise PaymentProviderVerificationError("شماره سفارش فاکتور TCart تطابق ندارد")
        payment_url = body.get("payment_url", "")
        parts = urlsplit(payment_url)
        if parts.scheme != "https" or parts.netloc != "tcartt.com":
            raise PaymentProviderVerificationError("لینک پرداخت TCart نامعتبر است")
        return PaymentStartResult(
            gateway_url=payment_url, provider_reference=str(invoice_id),
            provider_amount=unique, provider_currency="IRT", provider_adjustment_toman=unique - base,
            request_payload={k: v for k, v in payload.items() if k != "buyer_ref"},
            response_payload={k: body.get(k) for k in (
                "invoice_id", "tracking_code", "status", "base_price_toman", "unique_amount_toman", "expires_at", "external_order_id"
            )},
        )

    def verify_payment(self, *, attempt, callback_data) -> PaymentVerifyResult:
        invoice_id = self._positive_int(attempt.provider_reference, "invoice_id")
        url = self.invoice_status_url.replace("{invoice_id}", str(invoice_id))
        body = self._call("GET", url)
        # Never accept callback status as proof of payment.
        details = body.get("invoice") if isinstance(body.get("invoice"), dict) else body
        if "invoice_id" in details and str(details["invoice_id"]) != str(invoice_id):
            raise PaymentProviderVerificationError("شناسه فاکتور TCart تطابق ندارد")
        if "external_order_id" in details and str(details["external_order_id"]) != str(attempt.order.order_number):
            raise PaymentProviderVerificationError("شماره سفارش TCart تطابق ندارد")
        if "base_price_toman" in details and self._positive_int(details["base_price_toman"], "base_price_toman") != int(attempt.amount_toman):
            raise PaymentProviderVerificationError("مبلغ پایه TCart تطابق ندارد")
        if "unique_amount_toman" in details and self._positive_int(details["unique_amount_toman"], "unique_amount_toman") != int(attempt.provider_amount):
            raise PaymentProviderVerificationError("مبلغ یکتای TCart تطابق ندارد")
        status_value = str(details.get("status", "")).lower()
        if status_value not in ("pending", "paid", "expired", "cancelled"):
            raise PaymentProviderVerificationError("وضعیت فاکتور TCart ناشناخته است")
        sanitized = {key: details.get(key) for key in (
            "invoice_id", "tracking_code", "external_order_id", "base_price_toman", "unique_amount_toman", "status", "paid_at"
        )}
        if status_value == "paid":
            if not details.get("paid_at"):
                raise PaymentProviderVerificationError("فاکتور پرداخت‌شده فاقد paid_at است")
            # If amount fields absent, fail closed: cannot prove correct settlement.
            if "base_price_toman" not in details or "unique_amount_toman" not in details or "external_order_id" not in details:
                raise PaymentProviderVerificationError("اطلاعات مالی وضعیت فاکتور ناقص است")
            return PaymentVerifyResult(success=True, provider_transaction_id=str(details.get("tracking_code") or invoice_id), response_payload=sanitized)
        return PaymentVerifyResult(success=False, failure_code=status_value, failure_message=f"TCart status: {status_value}", response_payload=sanitized)
