from __future__ import annotations

from typing import Any

import requests
from requests import Response
from requests.exceptions import (
    ConnectionError,
    RequestException,
    Timeout,
)

from .config import SMSConfig


class MeliPayamakError(Exception):
    """Base exception for MeliPayamak errors."""


class MeliPayamakConnectionError(MeliPayamakError):
    """Raised when connection to MeliPayamak fails."""


class MeliPayamakTimeoutError(MeliPayamakError):
    """Raised when MeliPayamak request times out."""


class MeliPayamakAPIError(MeliPayamakError):
    """Raised when MeliPayamak returns an API error."""


class MeliPayamakClient:
    """
    Client for MeliPayamak REST API.

    No database is used by this class.

    Configuration comes from:

        MELIPAYAMAK_API_TOKEN
        MELIPAYAMAK_DEFAULT_FROM
    """

    BASE_URL = (
        "https://console.melipayamak.com/api"
    )

    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        timeout: int | float | None = None,
    ) -> None:

        config = SMSConfig.get()

        self.api_token = config["API_TOKEN"]
        self.default_from = config["DEFAULT_FROM"]

        self.timeout = (
            timeout
            if timeout is not None
            else self.DEFAULT_TIMEOUT
        )

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    # =========================================================
    # INTERNAL
    # =========================================================

    def _url(self, path: str) -> str:
        """
        Build MeliPayamak URL.

        The API token is part of the URL according
        to the official API documentation.
        """

        path = path.strip("/")

        return (
            f"{self.BASE_URL}/"
            f"{path}/"
            f"{self.api_token}"
        )

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute HTTP request.
        """

        url = self._url(path)

        try:

            if method.upper() == "GET":

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                )

            else:

                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    json=data or {},
                    timeout=self.timeout,
                )

        except Timeout as exc:

            raise MeliPayamakTimeoutError(
                "MeliPayamak request timed out."
            ) from exc

        except ConnectionError as exc:

            raise MeliPayamakConnectionError(
                "Could not connect to MeliPayamak."
            ) from exc

        except RequestException as exc:

            raise MeliPayamakConnectionError(
                f"MeliPayamak request failed: {exc}"
            ) from exc

        return self._handle_response(response)

    def _handle_response(
        self,
        response: Response,
    ) -> Any:
        """
        Parse MeliPayamak response.

        MeliPayamak normally returns JSON containing
        a status field.
        """

        try:

            data = response.json()

        except ValueError as exc:

            raise MeliPayamakAPIError(
                "MeliPayamak returned invalid JSON."
            ) from exc

        if not response.ok:

            raise MeliPayamakAPIError(
                self._extract_error(
                    data,
                    response.status_code,
                )
            )

        return data

    @staticmethod
    def _extract_error(
        data: Any,
        status_code: int,
    ) -> str:

        if isinstance(data, dict):

            for key in (
                "status",
                "message",
                "Message",
                "error",
                "Error",
            ):

                value = data.get(key)

                if value:
                    return str(value)

        return (
            "MeliPayamak request failed "
            f"with HTTP {status_code}."
        )

    # =========================================================
    # SEND - OTP
    # =========================================================

    def send_otp(
        self,
        to: str,
    ) -> Any:
        """
        Send OTP SMS.

        Official endpoint:

        /api/send/otp/{API_TOKEN}

        Payload:

        {
            "to": "09123456789"
        }
        """

        return self._request(
            "POST",
            "send/otp",
            {
                "to": to,
            },
        )

    # =========================================================
    # SEND - SIMPLE
    # =========================================================

    def send_simple(
        self,
        to: str,
        text: str,
        from_number: str | None = None,
    ) -> Any:
        """
        Send simple SMS.

        Official endpoint:

        /api/send/simple/{API_TOKEN}

        Payload:

        {
            "from": "5000xxx",
            "to": "09123456789",
            "text": "test sms"
        }
        """

        sender = (
            from_number
            or self.default_from
        )

        return self._request(
            "POST",
            "send/simple",
            {
                "from": sender,
                "to": to,
                "text": text,
            },
        )

    # =========================================================
    # SEND - SCHEDULE
    # =========================================================

    def send_schedule(
        self,
        message: str,
        to: str,
        date: str,
        from_number: str | None = None,
        period: int | None = None,
    ) -> Any:
        """
        Send scheduled SMS.

        Official endpoint:

        /api/send/schedule/{API_TOKEN}
        """

        sender = (
            from_number
            or self.default_from
        )

        data: dict[str, Any] = {
            "message": message,
            "from": sender,
            "to": to,
            "date": date,
        }

        if period is not None:
            data["period"] = period

        return self._request(
            "POST",
            "send/schedule",
            data,
        )

    # =========================================================
    # SEND - ADVANCED
    # =========================================================

    def send_advanced(
        self,
        to: list[str],
        text: str,
        from_number: str | None = None,
        udh: str = "",
    ) -> Any:
        """
        Send one text to multiple recipients.

        Official endpoint:

        /api/send/advanced/{API_TOKEN}
        """

        sender = (
            from_number
            or self.default_from
        )

        return self._request(
            "POST",
            "send/advanced",
            {
                "from": sender,
                "to": to,
                "text": text,
                "udh": udh,
            },
        )

    # =========================================================
    # SEND - SHARED
    # =========================================================

    def send_shared(
        self,
        body_id: int,
        to: str,
        args: list[str] | None = None,
    ) -> Any:
        """
        Send SMS using shared service line.

        Official endpoint:

        /api/send/shared/{API_TOKEN}
        """

        return self._request(
            "POST",
            "send/shared",
            {
                "bodyId": body_id,
                "to": to,
                "args": args or [],
            },
        )

    # =========================================================
    # SEND - MULTIPLE
    # =========================================================

    def send_multiple(
        self,
        to: list[str],
        text: list[str],
        from_number: str | None = None,
        udh: str = "",
    ) -> Any:
        """
        Send different text to different recipients.

        Official endpoint:

        /api/send/multiple/{API_TOKEN}
        """

        sender = (
            from_number
            or self.default_from
        )

        return self._request(
            "POST",
            "send/multiple",
            {
                "from": sender,
                "to": to,
                "text": text,
                "udh": udh,
            },
        )

    # =========================================================
    # RECEIVE - STATUS
    # =========================================================

    def delivery_status(
        self,
        rec_ids: list[int],
    ) -> Any:
        """
        Get delivery status.

        Official endpoint:

        /api/receive/status/{API_TOKEN}
        """

        return self._request(
            "POST",
            "receive/status",
            {
                "recIds": rec_ids,
            },
        )

    # =========================================================
    # RECEIVE - MESSAGES
    # =========================================================

    def messages(
        self,
        message_type: str,
        number: str,
        index: int = 0,
        count: int = 100,
    ) -> Any:
        """
        Get received/sent messages.

        message_type:
            in
            out
            all
        """

        return self._request(
            "POST",
            "receive/messages",
            {
                "type": message_type,
                "number": number,
                "index": index,
                "count": count,
            },
        )

    # =========================================================
    # RECEIVE - INBOX COUNT
    # =========================================================

    def inbox_count(
        self,
        is_read: bool = False,
    ) -> Any:
        """
        Get inbox message count.
        """

        return self._request(
            "POST",
            "receive/inboxcount",
            {
                "isRead": is_read,
            },
        )

    # =========================================================
    # ACCOUNT - CREDIT
    # =========================================================

    def credit(self) -> Any:
        """
        Get SMS credit.

        This endpoint uses GET.
        """

        return self._request(
            "GET",
            "receive/credit",
        )

    # =========================================================
    # ACCOUNT - PRICE
    # =========================================================

    def price(
        self,
        mtn_count: int,
        irancell_count: int,
        text: str,
        from_number: str | None = None,
    ) -> Any:
        """
        Calculate SMS price.
        """

        sender = (
            from_number
            or self.default_from
        )

        return self._request(
            "POST",
            "receive/price",
            {
                "mtnCount": mtn_count,
                "irancellCount": irancell_count,
                "from": sender,
                "text": text,
            },
        )

    # =========================================================
    # HEALTH
    # =========================================================

    def health(self) -> dict[str, Any]:
        """
        Basic health information.

        This method does not store anything in DB.
        """

        credit = self.credit()

        inbox = self.inbox_count(
            is_read=False,
        )

        return {
            "connected": True,
            "credit": credit,
            "inbox": inbox,
        }

    # =========================================================
    # SESSION
    # =========================================================

    def close(self) -> None:
        """
        Close HTTP session.
        """

        self.session.close()

    def __enter__(
        self,
    ) -> "MeliPayamakClient":

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.close()