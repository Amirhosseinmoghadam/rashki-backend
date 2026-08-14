from __future__ import annotations

from django.conf import settings

from .client import MeliPayamakClient
from .exceptions import SMSValidationError


class SMSSender:

    @staticmethod
    def _get_default_from() -> str:
        config = getattr(settings, "MELIPAYAMAK", {})

        sender = config.get(
            "DEFAULT_FROM",
            "",
        )

        if not sender:
            raise SMSValidationError(
                "MELIPAYAMAK['DEFAULT_FROM'] is not configured."
            )

        return sender

    @staticmethod
    def _validate_phone(phone: str) -> str:
        phone = str(phone).strip()

        if not phone:
            raise SMSValidationError(
                "Recipient phone number is required."
            )

        return phone

    @classmethod
    def otp(
        cls,
        to: str,
    ):
        """
        Send one-time password SMS.
        """

        to = cls._validate_phone(to)

        client = MeliPayamakClient()

        return client.send_otp(to)

    @classmethod
    def simple(
        cls,
        *,
        to: str,
        text: str,
        from_number: str | None = None,
    ):
        """
        Send a normal SMS to one recipient.
        """

        to = cls._validate_phone(to)

        if not text:
            raise SMSValidationError(
                "SMS text is required."
            )

        from_number = (
            from_number
            or cls._get_default_from()
        )

        client = MeliPayamakClient()

        return client.send_simple(
            from_number=from_number,
            to=to,
            text=text,
        )

    @classmethod
    def advanced(
        cls,
        *,
        to: list[str],
        text: str,
        from_number: str | None = None,
        udh: str = "",
    ):
        """
        Send the same SMS to multiple recipients.
        """

        if not to:
            raise SMSValidationError(
                "Recipients are required."
            )

        recipients = [
            cls._validate_phone(phone)
            for phone in to
        ]

        if not text:
            raise SMSValidationError(
                "SMS text is required."
            )

        from_number = (
            from_number
            or cls._get_default_from()
        )

        client = MeliPayamakClient()

        return client.send_advanced(
            from_number=from_number,
            to=recipients,
            text=text,
            udh=udh,
        )

    @classmethod
    def shared(
        cls,
        *,
        to: str,
        body_id: int,
        args: list[str] | None = None,
    ):
        """
        Send a predefined/shared-service SMS.
        """

        to = cls._validate_phone(to)

        if not body_id:
            raise SMSValidationError(
                "body_id is required."
            )

        client = MeliPayamakClient()

        return client.send_shared(
            body_id=body_id,
            to=to,
            args=args or [],
        )

    @classmethod
    def multiple(
        cls,
        *,
        to: list[str],
        text: list[str],
        from_number: str | None = None,
        udh: str = "",
    ):
        """
        Send a different text to each recipient.
        """

        if not to:
            raise SMSValidationError(
                "Recipients are required."
            )

        if not text:
            raise SMSValidationError(
                "Texts are required."
            )

        if len(to) != len(text):
            raise SMSValidationError(
                "Recipients and texts must have the same length."
            )

        recipients = [
            cls._validate_phone(phone)
            for phone in to
        ]

        from_number = (
            from_number
            or cls._get_default_from()
        )

        client = MeliPayamakClient()

        return client.send_multiple(
            from_number=from_number,
            to=recipients,
            text=text,
            udh=udh,
        )

    @classmethod
    def schedule(
        cls,
        *,
        to: str,
        message: str,
        date: str,
        from_number: str | None = None,
        period: int | None = None,
    ):
        """
        Schedule an SMS.
        """

        to = cls._validate_phone(to)

        if not message:
            raise SMSValidationError(
                "Message is required."
            )

        if not date:
            raise SMSValidationError(
                "Date is required."
            )

        from_number = (
            from_number
            or cls._get_default_from()
        )

        client = MeliPayamakClient()

        return client.send_schedule(
            message=message,
            from_number=from_number,
            to=to,
            date=date,
            period=period,
        )