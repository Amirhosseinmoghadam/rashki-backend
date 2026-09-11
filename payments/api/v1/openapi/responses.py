# =========================================================
# Payment Attempt
# =========================================================


PaymentAttemptExample = {
    "public_id": (
        "73dd90e4-26bf-4fb6-90f8-ad2e31ee47ea"
    ),

    "order_number": (
        "RK-20260909-A84F123B"
    ),

    "provider": "zarinpal",

    "status": "pending",

    "amount_toman": 2500000,

    "provider_amount": 2500000,

    "provider_currency": "IRT",

    "provider_adjustment_toman": 0,

    "provider_reference": (
        "A00000000000000000000000000000000001"
    ),

    "provider_transaction_id": "",

    "gateway_url": (
        "https://www.zarinpal.com/"
        "pg/StartPay/"
        "A00000000000000000000000000000000001"
    ),

    "started_at": (
        "2026-09-09T18:00:00Z"
    ),

    "expires_at": (
        "2026-09-09T18:20:00Z"
    ),

    "verified_at": None,

    "failed_at": None,

    "created_at": (
        "2026-09-09T18:00:00Z"
    ),

    "updated_at": (
        "2026-09-09T18:00:00Z"
    ),
}


# =========================================================
# Payment Responses
# =========================================================


PaymentStartSuccess = {
    "success": True,
    "message": (
        "درخواست پرداخت "
        "با موفقیت ایجاد شد."
    ),
    "data": PaymentAttemptExample,
}


PaymentAlreadyPaid = {
    "success": False,
    "message": (
        "این سفارش قبلاً پرداخت شده است."
    ),
    "errors": None,
}


PaymentExpiredOrder = {
    "success": False,
    "message": (
        "مهلت پرداخت این سفارش "
        "تمام شده است."
    ),
    "errors": None,
}


PaymentProviderError = {
    "success": False,
    "message": (
        "ارتباط با زرین‌پال "
        "امکان‌پذیر نبود."
    ),
    "errors": None,
}


TCartNotConfigured = {
    "success": False,
    "message": (
        "TCart در معماری فعال است، "
        "اما API Contract دقیق ساخت Invoice "
        "هنوز پیکربندی نشده است."
    ),
    "errors": None,
}


PaymentNotFound = {
    "success": False,
    "message": (
        "پرداخت موردنظر یافت نشد."
    ),
    "errors": None,
}


# =========================================================
# Refund Example
# =========================================================


PaymentRefundExample = {
    "public_id": (
        "1475dd9a-9c0c-4a36-a7b9-b2e19c00e055"
    ),

    "order_number": (
        "RK-20260909-A84F123B"
    ),

    "payment_public_id": (
        "eaac5c97-ab82-4ee6-aacf-995d5f37e790"
    ),

    "provider": "zarinpal",

    "status": "created",

    "amount_toman": 2500000,

    "provider_amount": None,

    "provider_currency": "IRT",

    "provider_session_id": "",

    "provider_refund_id": "",

    "reason": "customer_request",

    "description": (
        "لغو سفارش و بازپرداخت کامل مبلغ."
    ),

    "request_payload": {},

    "response_payload": {},

    "failure_code": "",

    "failure_message": "",

    "requested_at": None,

    "completed_at": None,

    "failed_at": None,

    "created_at": (
        "2026-09-09T18:30:00Z"
    ),

    "updated_at": (
        "2026-09-09T18:30:00Z"
    ),
}


# =========================================================
# Refund Created
# =========================================================


PaymentRefundCreated = {
    "success": True,

    "message": (
        "درخواست بازپرداخت "
        "با موفقیت ایجاد شد."
    ),

    "data": PaymentRefundExample,
}


# =========================================================
# Refund Existing / Idempotent
# =========================================================


PaymentRefundAlreadyExists = {
    "success": True,

    "message": (
        "درخواست بازپرداخت قبلاً "
        "وجود داشت."
    ),

    "data": PaymentRefundExample,
}


# =========================================================
# Refund Detail
# =========================================================


PaymentRefundDetail = {
    "success": True,

    "message": (
        "اطلاعات بازپرداخت دریافت شد."
    ),

    "data": PaymentRefundExample,
}


# =========================================================
# Refund Executed
# =========================================================


PaymentRefundExecuted = {
    "success": True,

    "message": (
        "بازپرداخت با موفقیت انجام شد."
    ),

    "data": {
        **PaymentRefundExample,

        "status": "succeeded",

        "provider_amount": 2500000,

        "request_payload": {
            "operation": "reversal",
            "amount_toman": 2500000,
            "provider": "zarinpal",
        },

        "response_payload": {
            "success": True,
            "code": 100,
            "message": (
                "Reversal successful"
            ),
        },

        "requested_at": (
            "2026-09-09T18:31:00Z"
        ),

        "completed_at": (
            "2026-09-09T18:31:01Z"
        ),

        "updated_at": (
            "2026-09-09T18:31:01Z"
        ),
    },
}


# =========================================================
# Refund Errors
# =========================================================


PaymentRefundOrderNotFound = {
    "success": False,

    "message": (
        "سفارش موردنظر یافت نشد."
    ),

    "errors": None,
}


PaymentRefundNotFound = {
    "success": False,

    "message": (
        "بازپرداخت موردنظر یافت نشد."
    ),

    "errors": None,
}


PaymentRefundNoSuccessfulPayment = {
    "success": False,

    "message": (
        "برای این سفارش PaymentAttempt "
        "موفق پیدا نشد."
    ),

    "errors": None,
}


PaymentRefundOverAmount = {
    "success": False,

    "message": (
        "مبلغ Refund از مبلغ قابل "
        "بازپرداخت بیشتر است."
    ),

    "errors": None,
}


PaymentRefundAlreadyFullyReserved = {
    "success": False,

    "message": (
        "تمام مبلغ این پرداخت قبلاً "
        "Refund شده یا برای Refund "
        "رزرو شده است."
    ),

    "errors": None,
}


# =========================================================
# Requires Review
# =========================================================


PaymentRefundRequiresReview = {
    "success": False,

    "message": (
        "نتیجه Refund نامشخص است. "
        "Retry خودکار انجام نشود."
    ),

    "data": {
        **PaymentRefundExample,

        "status": "requires_review",

        "failure_code": (
            "provider_result_unknown"
        ),

        "failure_message": (
            "نتیجه عملیات مالی Provider "
            "به دلیل خطای ارتباطی نامشخص است."
        ),

        "requested_at": (
            "2026-09-09T18:31:00Z"
        ),
    },

    "errors": None,
}


# =========================================================
# Provider Rejected
# =========================================================


PaymentRefundProviderRejected = {
    "success": False,

    "message": (
        "Provider درخواست Refund "
        "را رد کرد."
    ),

    "data": {
        **PaymentRefundExample,

        "status": "failed",

        "failure_code": (
            "provider_rejected"
        ),

        "failure_message": (
            "Provider درخواست Refund "
            "را رد کرد."
        ),

        "failed_at": (
            "2026-09-09T18:31:00Z"
        ),
    },

    "errors": None,
}


# =========================================================
# Permission
# =========================================================


PaymentRefundPermissionDenied = {
    "detail": (
        "شما اجازه انجام این دستور را ندارید."
    )
}


PaymentAuthenticationRequired = {
    "detail": (
        "اطلاعات برای احراز هویت ارائه نشده است."
    )
}