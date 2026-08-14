from __future__ import annotations

from django.conf import settings

from .client import MeliPayamakClient
from .exceptions import SMSValidationError


class SMSAccount:

    @staticmethod
    def credit():
        """
        Get current SMS panel credit.
        """

        return MeliPayamakClient().credit()

    @staticmethod
    def inbox_count(
        is_read: bool = False,
    ):
        """
        Get current inbox count.
        """

        return MeliPayamakClient().inbox_count(
            is_read=is_read
        )

    @staticmethod
    def price(
        *,
        mtn_count: int,
        irancell_count: int,
        text: str,
        from_number: str | None = None,
    ):
        """
        Calculate SMS sending price.
        """

        config = getattr(
            settings,
            "MELIPAYAMAK",
            {},
        )

        from_number = (
            from_number
            or config.get("DEFAULT_FROM")
        )

        if not from_number:
            raise SMSValidationError(
                "MELIPAYAMAK['DEFAULT_FROM'] is not configured."
            )

        return MeliPayamakClient().price(
            mtn_count=mtn_count,
            irancell_count=irancell_count,
            from_number=from_number,
            text=text,
        )

    @classmethod
    def health(cls):
        """
        Live health check.

        No database/cache/file is used.
        """

        credit = cls.credit()

        unread = cls.inbox_count(
            is_read=False
        )

        return {
            "ok": True,
            "credit": credit,
            "unread": unread,
        }