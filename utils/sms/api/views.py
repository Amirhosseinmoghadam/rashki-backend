from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)

from ..client import (
    MeliPayamakAPIError,
    MeliPayamakClient,
    MeliPayamakConnectionError,
    MeliPayamakError,
    MeliPayamakTimeoutError,
)

from .serializers import (
    AdvancedSMSSerializer,
    DeliveryStatusSerializer,
    InboxCountSerializer,
    MessagesSerializer,
    MultipleSMSSerializer,
    OTPSerializer,
    PriceSerializer,
    ScheduleSMSSerializer,
    SharedSMSSerializer,
    SimpleSMSSerializer,
)


class SMSAPIView(APIView):
    """
    Base view for SMS API.

    No database/model is used.
    """

    permission_classes = [AllowAny]

    def success(
        self,
        data,
        http_status=status.HTTP_200_OK,
    ):
        return Response(
            {
                "success": True,
                "data": data,
            },
            status=http_status,
        )

    def error(
        self,
        exc,
    ):
        if isinstance(
            exc,
            MeliPayamakTimeoutError,
        ):
            http_status = (
                status.HTTP_504_GATEWAY_TIMEOUT
            )

        elif isinstance(
            exc,
            MeliPayamakConnectionError,
        ):
            http_status = (
                status.HTTP_503_SERVICE_UNAVAILABLE
            )

        elif isinstance(
            exc,
            (
                MeliPayamakAPIError,
                MeliPayamakError,
            ),
        ):
            http_status = (
                status.HTTP_400_BAD_REQUEST
            )

        else:
            http_status = (
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "success": False,
                "error": str(exc),
            },
            status=http_status,
        )


# ============================================================
# OTP
# ============================================================


class SendOTPAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Send OTP",
        request=OTPSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = OTPSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_otp(
                    to=serializer.validated_data["to"]
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# SIMPLE
# ============================================================


class SendSimpleAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Send simple SMS",
        request=SimpleSMSSerializer,
        responses={
            200: OpenApiResponse(
                description=(
                    "MeliPayamak response containing "
                    "recId and status."
                ),
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = SimpleSMSSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_simple(
                    to=serializer.validated_data["to"],
                    text=serializer.validated_data["text"],
                    from_number=serializer.validated_data.get(
                        "from"
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# SCHEDULE
# ============================================================


class SendScheduleAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Schedule SMS",
        request=ScheduleSMSSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = ScheduleSMSSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_schedule(
                    message=serializer.validated_data[
                        "message"
                    ],
                    to=serializer.validated_data[
                        "to"
                    ],
                    date=serializer.validated_data[
                        "date"
                    ],
                    from_number=serializer.validated_data.get(
                        "from"
                    ),
                    period=serializer.validated_data.get(
                        "period"
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# ADVANCED
# ============================================================


class SendAdvancedAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Send advanced SMS",
        request=AdvancedSMSSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = AdvancedSMSSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_advanced(
                    to=serializer.validated_data[
                        "to"
                    ],
                    text=serializer.validated_data[
                        "text"
                    ],
                    from_number=serializer.validated_data.get(
                        "from"
                    ),
                    udh=serializer.validated_data.get(
                        "udh",
                        "",
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# SHARED
# ============================================================


class SendSharedAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Send shared SMS",
        request=SharedSMSSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = SharedSMSSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_shared(
                    body_id=serializer.validated_data[
                        "bodyId"
                    ],
                    to=serializer.validated_data[
                        "to"
                    ],
                    args=serializer.validated_data.get(
                        "args",
                        [],
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# MULTIPLE
# ============================================================


class SendMultipleAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Send"],
        summary="Send multiple SMS",
        request=MultipleSMSSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = MultipleSMSSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.send_multiple(
                    to=serializer.validated_data[
                        "to"
                    ],
                    text=serializer.validated_data[
                        "text"
                    ],
                    from_number=serializer.validated_data.get(
                        "from"
                    ),
                    udh=serializer.validated_data.get(
                        "udh",
                        "",
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# DELIVERY STATUS
# ============================================================


class DeliveryStatusAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Receive"],
        summary="Get delivery status",
        request=DeliveryStatusSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = DeliveryStatusSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.delivery_status(
                    rec_ids=serializer.validated_data[
                        "recIds"
                    ],
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# MESSAGES
# ============================================================


class MessagesAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Receive"],
        summary="Get SMS messages",
        request=MessagesSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = MessagesSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.messages(
                    message_type=serializer.validated_data[
                        "type"
                    ],
                    number=serializer.validated_data[
                        "number"
                    ],
                    index=serializer.validated_data[
                        "index"
                    ],
                    count=serializer.validated_data[
                        "count"
                    ],
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# INBOX COUNT
# ============================================================


class InboxCountAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Receive"],
        summary="Get inbox count",
        request=InboxCountSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = InboxCountSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.inbox_count(
                    is_read=serializer.validated_data[
                        "isRead"
                    ],
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# CREDIT
# ============================================================


class CreditAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Account"],
        summary="Get SMS credit",
        request=None,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak credit response.",
            ),
            400: OpenApiResponse(
                description="MeliPayamak error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def get(self, request):

        try:
            with MeliPayamakClient() as client:

                result = client.credit()

            return self.success(result)

        except Exception as exc:
            return self.error(exc)


# ============================================================
# PRICE
# ============================================================


class PriceAPIView(SMSAPIView):

    @extend_schema(
        tags=["SMS / Account"],
        summary="Calculate SMS price",
        request=PriceSerializer,
        responses={
            200: OpenApiResponse(
                description="MeliPayamak price response.",
            ),
            400: OpenApiResponse(
                description="Invalid request or API error.",
            ),
            503: OpenApiResponse(
                description="MeliPayamak connection error.",
            ),
            504: OpenApiResponse(
                description="MeliPayamak timeout.",
            ),
        },
    )
    def post(self, request):

        serializer = PriceSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            with MeliPayamakClient() as client:

                result = client.price(
                    mtn_count=serializer.validated_data[
                        "mtnCount"
                    ],
                    irancell_count=serializer.validated_data[
                        "irancellCount"
                    ],
                    text=serializer.validated_data[
                        "text"
                    ],
                    from_number=serializer.validated_data.get(
                        "from"
                    ),
                )

            return self.success(result)

        except Exception as exc:
            return self.error(exc)