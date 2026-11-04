"""TCart provider adapter.

IMPORTANT: Configure the exact TCart API contract from official merchant documentation.
No endpoint paths, auth headers, or JSON field names are assumed by this adapter.
Payment verification is based solely on a server-to-server status response, never
on the browser/webhook request body.
"""
from urllib.parse import urlsplit, quote

import requests
from django.conf import settings

from .base import (
    BasePaymentProvider,
    PaymentProviderConfigurationError,
    PaymentProviderRequestError,
    PaymentProviderVerificationError,
    PaymentProviderIndeterminateError,
    PaymentStartResult,
    PaymentVerifyResult,
)


def _require(value, label):
    if not value:
        raise PaymentProviderConfigurationError(f"TCart: {label} is not configured")
    return value


def _https(url, label):
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password or parts.fragment:
        raise PaymentProviderConfigurationError(f"TCart: {label} must be an HTTPS URL")
    return url


def _field(data, dotted_key):
    current = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


class TCartProvider(BasePaymentProvider):
    key = "tcart"
    provider_currency = "IRT"

    def __init__(self):
        # These settings intentionally have no speculative defaults.
        self.api_token = getattr(settings, "TCART_API_TOKEN", "")
        self.create_url = getattr(settings, "TCART_CREATE_INVOICE_URL", "")
        self.status_url_template = getattr(settings, "TCART_INVOICE_STATUS_URL", "")
        self.auth_header = getattr(settings, "TCART_AUTH_HEADER", "")
        self.auth_prefix = getattr(settings, "TCART_AUTH_PREFIX", "")
        self.request_fields = getattr(settings, "TCART_CREATE_FIELDS", {})
        self.response_fields = getattr(settings, "TCART_RESPONSE_FIELDS", {})
        self.status_fields = getattr(settings, "TCART_STATUS_FIELDS", {})
        self.paid_values = getattr(settings, "TCART_PAID_VALUES", ())
        self.timeout = float(getattr(settings, "TCART_HTTP_TIMEOUT", 10))

    def _headers(self):
        _require(self.api_token, "API token")
        _require(self.auth_header, "auth header")
        return {
            self.auth_header: f"{self.auth_prefix}{self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _contract(self):
        _https(_require(self.create_url, "create URL"), "create URL")
        _require(self.status_url_template, "status URL template")
        for key in ("amount", "order_id", "callback_url"):
            _require(self.request_fields.get(key), f"create field {key}")
        for key in ("invoice_id", "payment_url"):
            _require(self.response_fields.get(key), f"response field {key}")
        for key in ("status", "amount", "invoice_id"):
            _require(self.status_fields.get(key), f"status field {key}")
        _require(self.paid_values, "paid status values")

    @staticmethod
    def _parse(response):
        try:
            obj = response.json()
        except ValueError as exc:
            raise PaymentProviderVerificationError("TCart returned non-JSON response") from exc
        if not isinstance(obj, dict):
            raise PaymentProviderVerificationError("TCart JSON response must be an object")
        return obj

    def start_payment(self, *, attempt, callback_url) -> PaymentStartResult:
        self._contract()
        amount = self.convert_toman_to_provider_amount(attempt.amount_toman)
        payload = {
            self.request_fields["amount"]: amount,
            self.request_fields["order_id"]: str(attempt.public_id),
            self.request_fields["callback_url"]: callback_url,
        }
        # Never automatically retry an invoice creation POST after a timeout.
        try:
            resp = requests.post(
                self.create_url, json=payload, headers=self._headers(), timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise PaymentProviderIndeterminateError("TCart invoice creation result is unknown; review before retry") from exc
        if resp.status_code not in (200, 201):
            raise PaymentProviderRequestError(f"TCart rejected invoice creation (HTTP {resp.status_code})")
        data = self._parse(resp)
        invoice_id = _field(data, self.response_fields["invoice_id"])
        payment_url = _field(data, self.response_fields["payment_url"])
        if not isinstance(invoice_id, (str, int)) or not str(invoice_id).strip():
            raise PaymentProviderIndeterminateError("TCart creation response lacks invoice ID")
        if not isinstance(payment_url, str):
            raise PaymentProviderIndeterminateError("TCart creation response lacks payment URL")
        _https(payment_url, "payment URL")
        # TCart may assign a unique amount. Require an explicit mapping if it does.
        actual_amount = amount
        amount_field = self.response_fields.get("amount")
        if amount_field:
            raw_amount = _field(data, amount_field)
            try:
                actual_amount = int(raw_amount)
            except (ValueError, TypeError) as exc:
                raise PaymentProviderIndeterminateError("TCart response amount is invalid") from exc
            if actual_amount < amount:
                raise PaymentProviderIndeterminateError("TCart response amount is below order total")
        return PaymentStartResult(
            gateway_url=payment_url,
            provider_reference=str(invoice_id),
            provider_amount=actual_amount,
            provider_currency="IRT",
            provider_adjustment_toman=actual_amount - amount,
            request_payload={"amount": amount, "order_id": str(attempt.public_id)},
            response_payload={"invoice_id": str(invoice_id)},
        )

    def verify_payment(self, *, attempt, callback_data) -> PaymentVerifyResult:
        # callback_data is deliberately NOT used to prove payment.
        self._contract()
        invoice_id = str(attempt.provider_reference or "")
        _require(invoice_id, "stored invoice reference")
        if "{invoice_id}" not in self.status_url_template:
            raise PaymentProviderConfigurationError("TCart status URL must include {invoice_id}")
        url = _https(self.status_url_template.replace("{invoice_id}", quote(invoice_id, safe="")), "status URL")
        try:
            resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        except requests.RequestException as exc:
            raise PaymentProviderVerificationError("Unable to confirm TCart invoice status") from exc
        if resp.status_code != 200:
            raise PaymentProviderVerificationError(f"TCart status lookup failed (HTTP {resp.status_code})")
        data = self._parse(resp)
        actual_id = _field(data, self.status_fields["invoice_id"])
        actual_amount = _field(data, self.status_fields["amount"])
        actual_status = _field(data, self.status_fields["status"])
        if str(actual_id) != invoice_id:
            raise PaymentProviderVerificationError("TCart invoice reference mismatch")
        try:
            amount = int(actual_amount)
        except (TypeError, ValueError) as exc:
            raise PaymentProviderVerificationError("TCart invoice amount is invalid") from exc
        if amount != int(attempt.provider_amount):
            raise PaymentProviderVerificationError("TCart invoice amount mismatch")
        paid = str(actual_status) in {str(v) for v in self.paid_values}
        if not paid:
            # Without a documented terminal-failure status mapping, non-paid
            # states remain pending: raising preserves the current order status.
            raise PaymentProviderVerificationError("TCart invoice is not confirmed paid")
        transaction_field = self.status_fields.get("transaction_id")
        tx_id = _field(data, transaction_field) if transaction_field else None
        return PaymentVerifyResult(
            success=True,
            provider_transaction_id=str(tx_id or invoice_id),
            response_payload={"invoice_id": invoice_id, "status": str(actual_status), "amount": amount},
        )
