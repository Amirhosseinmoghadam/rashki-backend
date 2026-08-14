from rest_framework import serializers


# ============================================================
# SEND OTP
# ============================================================


class OTPSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/otp/{API_TOKEN}

    Request:
    {
        "to": "09123456789"
    }
    """

    to = serializers.CharField(
        max_length=20,
        help_text="Recipient mobile number.",
    )


# ============================================================
# SEND SIMPLE
# ============================================================


class SimpleSMSSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/simple/{API_TOKEN}

    Request:
    {
        "from": "5000xxx",
        "to": "09123456789",
        "text": "پیامک آزمایشی"
    }
    """

    from_number = serializers.CharField(
        source="from",
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="Sender number.",
    )

    to = serializers.CharField(
        max_length=20,
        help_text="Recipient mobile number.",
    )

    text = serializers.CharField(
        help_text="SMS text.",
    )


# ============================================================
# SEND SCHEDULE
# ============================================================


class ScheduleSMSSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/schedule/{API_TOKEN}

    Request:
    {
        "message": "پیامک زماندار",
        "from": "5000xxx",
        "to": "09123456789",
        "date": "1/20/2023 15:22",
        "period": 365
    }
    """

    message = serializers.CharField(
        help_text="SMS message.",
    )

    from_number = serializers.CharField(
        source="from",
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="Sender number.",
    )

    to = serializers.CharField(
        max_length=20,
        help_text="Recipient mobile number.",
    )

    date = serializers.CharField(
        help_text=(
            "Scheduled date/time. "
            "Example: 1/20/2023 15:22"
        ),
    )

    period = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text=(
            "Optional repeat period in days."
        ),
    )


# ============================================================
# SEND ADVANCED
# ============================================================


class AdvancedSMSSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/advanced/{API_TOKEN}

    Request:
    {
        "from": "5000xxx",
        "to": [
            "09123456789",
            "09123456789"
        ],
        "text": "پیامک آزمایشی",
        "udh": ""
    }
    """

    from_number = serializers.CharField(
        source="from",
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="Sender number.",
    )

    to = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
        ),
        min_length=1,
        help_text=(
            "One or more recipient numbers."
        ),
    )

    text = serializers.CharField(
        help_text="Same SMS text for recipients.",
    )

    udh = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text=(
            "Optional UDH for port-specific SMS."
        ),
    )


# ============================================================
# SEND SHARED
# ============================================================


class SharedSMSSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/shared/{API_TOKEN}

    Request:
    {
        "bodyId": 524,
        "to": "09123456789",
        "args": [
            "arg1",
            "arg2"
        ]
    }
    """

    body_id = serializers.IntegerField(
        source="bodyId",
        min_value=1,
        help_text="Approved shared message body ID.",
    )

    to = serializers.CharField(
        max_length=20,
        help_text="Recipient mobile number.",
    )

    args = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text=(
            "Variables used in the approved "
            "shared message body."
        ),
    )


# ============================================================
# SEND MULTIPLE
# ============================================================


class MultipleSMSSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/send/multiple/{API_TOKEN}

    Request:
    {
        "from": "5000xxx",
        "to": [
            "09123456789",
            "09123456789"
        ],
        "text": [
            "پیامک آزمایشی",
            "پیامک آزمایشی"
        ],
        "udh": ""
    }

    Each text corresponds to the recipient
    at the same index.
    """

    from_number = serializers.CharField(
        source="from",
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="Sender number.",
    )

    to = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
        ),
        min_length=1,
        help_text="Recipient numbers.",
    )

    text = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        help_text=(
            "SMS texts. Each text corresponds "
            "to the recipient at the same index."
        ),
    )

    udh = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text=(
            "Optional UDH for port-specific SMS."
        ),
    )

    def validate(self, attrs):
        """
        MeliPayamak requires one text per recipient.
        """

        if len(attrs["to"]) != len(attrs["text"]):
            raise serializers.ValidationError(
                {
                    "text": (
                        "The number of texts must "
                        "match the number of recipients."
                    )
                }
            )

        return attrs


# ============================================================
# DELIVERY STATUS
# ============================================================


class DeliveryStatusSerializer(
    serializers.Serializer,
):
    """
    MeliPayamak:
    POST /api/receive/status/{API_TOKEN}

    Request:
    {
        "recIds": [
            3741437414,
            3741537415
        ]
    }
    """

    rec_ids = serializers.ListField(
        source="recIds",
        child=serializers.IntegerField(),
        min_length=1,
        help_text=(
            "SMS record IDs returned after sending."
        ),
    )


# ============================================================
# RECEIVE MESSAGES
# ============================================================


class MessagesSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/receive/messages/{API_TOKEN}

    Request:
    {
        "type": "in",
        "number": "5000xxx",
        "index": 0,
        "count": 100
    }

    type:
        in
        out
        all
    """

    message_type = serializers.ChoiceField(
        source="type",
        choices=[
            ("in", "Incoming"),
            ("out", "Outgoing"),
            ("all", "All"),
        ],
        help_text=(
            "Message type: in, out or all."
        ),
    )

    number = serializers.CharField(
        max_length=30,
        help_text="SMS sender/line number.",
    )

    index = serializers.IntegerField(
        min_value=0,
        default=0,
        help_text="Pagination start index.",
    )

    count = serializers.IntegerField(
        min_value=1,
        default=100,
        help_text="Number of messages.",
    )


# ============================================================
# INBOX COUNT
# ============================================================


class InboxCountSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/receive/inboxcount/{API_TOKEN}

    Request:
    {
        "isRead": false
    }
    """

    is_read = serializers.BooleanField(
        source="isRead",
        default=False,
        help_text=(
            "true for read messages, "
            "false for unread messages."
        ),
    )


# ============================================================
# PRICE
# ============================================================


class PriceSerializer(serializers.Serializer):
    """
    MeliPayamak:
    POST /api/receive/price/{API_TOKEN}

    Request:
    {
        "mtnCount": 10,
        "irancellCount": 15,
        "from": "5000xxx",
        "text": "پیامک آزمایشی"
    }
    """

    mtn_count = serializers.IntegerField(
        source="mtnCount",
        min_value=0,
        help_text=(
            "Number of MCI recipients."
        ),
    )

    irancell_count = serializers.IntegerField(
        source="irancellCount",
        min_value=0,
        help_text=(
            "Number of Irancell recipients."
        ),
    )

    from_number = serializers.CharField(
        source="from",
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="Sender number.",
    )

    text = serializers.CharField(
        help_text="SMS text.",
    )