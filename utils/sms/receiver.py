from __future__ import annotations

from .client import MeliPayamakClient


class SMSReceiver:

    @staticmethod
    def delivery_status(
        rec_ids: list[int],
    ):
        """
        Get delivery status for SMS records.
        """

        return MeliPayamakClient().delivery_status(
            rec_ids
        )

    @staticmethod
    def messages(
        *,
        message_type: str = "all",
        number: str,
        index: int = 0,
        count: int = 100,
    ):
        """
        Get incoming/outgoing SMS messages.
        """

        if message_type not in {
            "in",
            "out",
            "all",
        }:
            raise ValueError(
                "message_type must be 'in', 'out' or 'all'."
            )

        return MeliPayamakClient().messages(
            message_type=message_type,
            number=number,
            index=index,
            count=count,
        )

    @staticmethod
    def inbox_count(
        is_read: bool = False,
    ):
        """
        Get SMS inbox count.
        """

        return MeliPayamakClient().inbox_count(
            is_read=is_read
        )