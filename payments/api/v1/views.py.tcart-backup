from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)

from rest_framework.response import Response

from orders.models import (
    Order,
)

from payments.models import (
    PaymentAttempt,
    PaymentRefund,
)

from payments.selectors import (
    get_user_payment_attempts,
)

from payments.services import (
    PaymentNotFoundError,
    PaymentRefundValidationError,
    PaymentValidationError,
    create_payment_refund,
    execute_payment_refund,
    process_payment_callback,
    start_payment,
)

from .serializers import (
    PaymentAttemptSerializer,
    PaymentRefundCreateSerializer,
    PaymentRefundSerializer,
    PaymentStartSerializer,
)

from .openapi.schema import (
    payment_detail_schema,
    payment_refund_create_schema,
    payment_refund_detail_schema,
    payment_refund_execute_schema,
    payment_start_schema,
    tcart_callback_schema,
    zarinpal_callback_schema,
)


# =========================================================
# Payment Detail
# =========================================================


class PaymentDetailAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        PaymentAttemptSerializer
    )

    @payment_detail_schema
    def get(
        self,
        request,
        public_id,
        *args,
        **kwargs,
    ):

        attempt = (
            get_user_payment_attempts(
                request.user
            )
            .filter(
                public_id=public_id
            )
            .first()
        )

        if attempt is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "پرداخت موردنظر یافت نشد."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            {
                "success": True,
                "message": (
                    "اطلاعات پرداخت دریافت شد."
                ),
                "data": (
                    PaymentAttemptSerializer(
                        attempt
                    ).data
                ),
            }
        )


# =========================================================
# ZarinPal Callback
# =========================================================


class ZarinPalCallbackAPIView(
    generics.GenericAPIView
):

    # Callback زرین‌پال از Browser کاربر می‌آید
    # و JWT ندارد.
    authentication_classes = []

    permission_classes = [
        AllowAny,
    ]

    @zarinpal_callback_schema
    def get(
        self,
        request,
        public_id,
        *args,
        **kwargs,
    ):

        try:

            attempt = process_payment_callback(
                public_id=public_id,

                provider_key=(
                    PaymentAttempt
                    .Provider
                    .ZARINPAL
                ),

                callback_data=(
                    request.query_params
                ),
            )

        except (
            PaymentNotFoundError,
            PaymentValidationError,
        ) as exc:

            query = urlencode(
                {
                    "success": "false",
                    "message": str(exc),
                }
            )

            return redirect(
                (
                    f"{settings.PAYMENT_FAILED_REDIRECT_URL}"
                    f"?{query}"
                )
            )

        if (
            attempt.status
            == PaymentAttempt.Status.SUCCEEDED
        ):

            query = urlencode(
                {
                    "success": "true",

                    "order": (
                        attempt
                        .order
                        .order_number
                    ),

                    "payment": (
                        str(
                            attempt.public_id
                        )
                    ),

                    "ref_id": (
                        attempt
                        .provider_transaction_id
                    ),
                }
            )

            return redirect(
                (
                    f"{settings.PAYMENT_SUCCESS_REDIRECT_URL}"
                    f"?{query}"
                )
            )

        query = urlencode(
            {
                "success": "false",

                "order": (
                    attempt
                    .order
                    .order_number
                ),

                "payment": (
                    str(
                        attempt.public_id
                    )
                ),
            }
        )

        return redirect(
            (
                f"{settings.PAYMENT_FAILED_REDIRECT_URL}"
                f"?{query}"
            )
        )


# =========================================================
# TCart Callback
# =========================================================


class TCartCallbackAPIView(
    generics.GenericAPIView
):

    authentication_classes = []

    permission_classes = [
        AllowAny,
    ]

    @tcart_callback_schema
    def post(
        self,
        request,
        public_id,
        *args,
        **kwargs,
    ):

        try:

            attempt = process_payment_callback(
                public_id=public_id,

                provider_key=(
                    PaymentAttempt
                    .Provider
                    .TCART
                ),

                callback_data=(
                    request.data
                ),
            )

        except PaymentNotFoundError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        except PaymentValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=(
                    status
                    .HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        return Response(
            {
                "success": True,

                "status": (
                    attempt.status
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Start Payment
# =========================================================


class PaymentStartAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        PaymentStartSerializer
    )

    @payment_start_schema
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        provider_key = (
            serializer.validated_data[
                "provider"
            ]
        )

        if (
            provider_key
            == PaymentAttempt
            .Provider
            .ZARINPAL
        ):

            callback_name = (
                "payments_api_v1:"
                "zarinpal-callback"
            )

        elif (
            provider_key
            == PaymentAttempt
            .Provider
            .TCART
        ):

            callback_name = (
                "payments_api_v1:"
                "tcart-callback"
            )

        else:

            return Response(
                {
                    "success": False,

                    "message": (
                        "روش پرداخت معتبر نیست."
                    ),

                    "errors": None,
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        def callback_url_builder(
            public_id,
        ):

            return (
                request
                .build_absolute_uri(
                    reverse(
                        callback_name,

                        kwargs={
                            "public_id": (
                                public_id
                            )
                        },
                    )
                )
            )

        try:

            attempt = start_payment(
                user=request.user,

                order_number=(
                    serializer
                    .validated_data[
                        "order_number"
                    ]
                ),

                provider_key=(
                    provider_key
                ),

                callback_url_builder=(
                    callback_url_builder
                ),

                idempotency_key=(
                    request.headers.get(
                        "Idempotency-Key"
                    )
                ),
            )

        except PaymentValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": None,
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "success": True,

                "message": (
                    "درخواست پرداخت "
                    "با موفقیت ایجاد شد."
                ),

                "data": (
                    PaymentAttemptSerializer(
                        attempt
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Create Refund
# =========================================================


class PaymentRefundCreateAPIView(
    generics.GenericAPIView
):
    """
    ایجاد رکورد Refund.

    فقط Admin اجازه ساخت Refund دارد.

    نکته:
        این endpoint هنوز عملیات مالی Provider
        را اجرا نمی‌کند.

        اجرای واقعی از Endpoint مجزای execute
        انجام می‌شود.
    """

    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = (
        PaymentRefundCreateSerializer
    )

    @payment_refund_create_schema
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = (
            Order.objects
            .filter(
                order_number=(
                    serializer
                    .validated_data[
                        "order_number"
                    ]
                )
            )
            .first()
        )

        if order is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "سفارش موردنظر یافت نشد."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        idempotency_key = (
            request.headers.get(
                "Idempotency-Key"
            )
        )

        # فقط برای تعیین 200/201 است.
        existing_before = False

        if idempotency_key:

            normalized_key = (
                str(
                    idempotency_key
                )
                .strip()
            )

            if normalized_key:

                existing_before = (
                    PaymentRefund.objects
                    .filter(
                        idempotency_key=(
                            normalized_key
                        )
                    )
                    .exists()
                )

        try:

            refund = create_payment_refund(
                order=order,

                amount_toman=(
                    serializer
                    .validated_data
                    .get(
                        "amount_toman"
                    )
                ),

                reason=(
                    serializer
                    .validated_data
                    .get(
                        "reason",
                        "",
                    )
                ),

                description=(
                    serializer
                    .validated_data
                    .get(
                        "description",
                        "",
                    )
                ),

                idempotency_key=(
                    idempotency_key
                ),
            )

        except PaymentRefundValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": None,
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "success": True,

                "message": (
                    "درخواست بازپرداخت قبلاً "
                    "وجود داشت."
                    if existing_before
                    else
                    "درخواست بازپرداخت "
                    "با موفقیت ایجاد شد."
                ),

                "data": (
                    PaymentRefundSerializer(
                        refund
                    ).data
                ),
            },
            status=(
                status.HTTP_200_OK
                if existing_before
                else status.HTTP_201_CREATED
            ),
        )


# =========================================================
# Refund Detail
# =========================================================


class PaymentRefundDetailAPIView(
    generics.GenericAPIView
):
    """
    مشاهده وضعیت Refund.

    به دلیل اطلاعات مالی:
        Admin-only
    """

    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = (
        PaymentRefundSerializer
    )

    @payment_refund_detail_schema
    def get(
        self,
        request,
        public_id,
        *args,
        **kwargs,
    ):

        refund = (
            PaymentRefund.objects
            .select_related(
                "order",
                "payment_attempt",
            )
            .filter(
                public_id=public_id
            )
            .first()
        )

        if refund is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "بازپرداخت موردنظر یافت نشد."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        return Response(
            {
                "success": True,

                "message": (
                    "اطلاعات بازپرداخت "
                    "دریافت شد."
                ),

                "data": (
                    PaymentRefundSerializer(
                        refund
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Execute Refund
# =========================================================


class PaymentRefundExecuteAPIView(
    generics.GenericAPIView
):
    """
    اجرای واقعی عملیات مالی Refund.

    Admin-only.

    این Endpoint عمداً از Create جداست تا:

        1. ساخت Refund قابل Audit باشد.
        2. اجرای عملیات مالی صریح باشد.
        3. Idempotency حفظ شود.
        4. REQUIRES_REVIEW قابل کنترل باشد.
    """

    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = (
        PaymentRefundSerializer
    )

    @payment_refund_execute_schema
    def post(
        self,
        request,
        public_id,
        *args,
        **kwargs,
    ):

        refund = (
            PaymentRefund.objects
            .select_related(
                "order",
                "payment_attempt",
            )
            .filter(
                public_id=public_id
            )
            .first()
        )

        if refund is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "بازپرداخت موردنظر یافت نشد."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        try:

            refund = execute_payment_refund(
                refund=refund
            )

        except PaymentRefundValidationError as exc:

            # وضعیت جدید را دوباره از DB می‌خوانیم.
            refund.refresh_from_db()

            # ---------------------------------------------
            # نتیجه عملیات مالی نامشخص
            # ---------------------------------------------

            if (
                refund.status
                == PaymentRefund
                .Status
                .REQUIRES_REVIEW
            ):

                response_status = (
                    status.HTTP_409_CONFLICT
                )

            # ---------------------------------------------
            # Provider قطعی Reject کرده
            # ---------------------------------------------

            elif (
                refund.status
                == PaymentRefund
                .Status
                .FAILED
            ):

                response_status = (
                    status.HTTP_502_BAD_GATEWAY
                )

            # ---------------------------------------------
            # Business Validation
            # ---------------------------------------------

            else:

                response_status = (
                    status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "success": False,
                    "message": str(exc),

                    "data": (
                        PaymentRefundSerializer(
                            refund
                        ).data
                    ),

                    "errors": None,
                },
                status=response_status,
            )

        return Response(
            {
                "success": True,

                "message": (
                    "بازپرداخت با موفقیت "
                    "انجام شد."
                ),

                "data": (
                    PaymentRefundSerializer(
                        refund
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )