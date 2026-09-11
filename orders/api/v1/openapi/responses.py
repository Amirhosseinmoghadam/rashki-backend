OrderExample = {
    "order_number": (
        "RK-20260904-A84F123B"
    ),

    "status": "pending_payment",

    "payment_status": "unpaid",

    "items": [
        {
            "id": 1,
            "product_id_snapshot": 25,
            "product_name": (
                "شمع NGK CPR6EA-9"
            ),
            "product_slug": (
                "شمع-ngk-cpr6ea-9"
            ),
            "product_sku": (
                "NGK-CPR6EA9"
            ),
            "product_brand_name": "NGK",
            "product_unit": "piece",
            "unit_price_toman": 590000,
            "quantity": 2,
            "total_price_toman": 1180000,
        }
    ],

    "subtotal_toman": 1180000,

    "eligible_discount_subtotal_toman": (
        1180000
    ),

    "discount_amount_toman": 236000,

    "shipping_amount_toman": 120000,

    "total_toman": 1064000,

    "discount_code": "OFF20",

    "discount_type": "percentage",

    "discount_scope": "all",

    "shipping_method_code": (
        "post-pishtaz"
    ),

    "shipping_method_name": (
        "پست پیشتاز"
    ),

    "shipping_provider": "post",

    "shipping_service_code": (
        "PISHTAZ"
    ),

    "shipping_weight_grams": 2350,

    "shipping_first_name": "امیرحسین",

    "shipping_last_name": "مقدم",

    "shipping_mobile_number": (
        "09123456789"
    ),

    "shipping_phone_number": (
        "02112345678"
    ),

    "shipping_province_name": "تهران",

    "shipping_city_name": "تهران",

    "shipping_postal_code": (
        "1234567890"
    ),

    "shipping_postal_address": (
        "تهران، ..."
    ),

    "customer_note": "",

    "terms_accepted_at": (
        "2026-09-04T18:00:00Z"
    ),

    "expires_at": (
        "2026-09-04T18:20:00Z"
    ),

    "paid_at": None,
    "cancelled_at": None,
    "shipped_at": None,
    "delivered_at": None,

    "created_at": (
        "2026-09-04T18:00:00Z"
    ),

    "updated_at": (
        "2026-09-04T18:00:00Z"
    ),
}


OrderCreateSuccess = {
    "success": True,
    "message": (
        "سفارش با موفقیت ثبت شد."
    ),
    "data": OrderExample,
}


OrderInvalidStock = {
    "success": False,
    "message": (
        "موجودی «شمع NGK CPR6EA-9» "
        "کافی نیست. موجودی فعلی "
        "1 عدد است."
    ),
    "errors": None,
}


OrderInvalidShipping = {
    "success": False,
    "message": (
        "روش ارسال معتبر نیست."
    ),
    "errors": None,
}


OrderInvalidAddress = {
    "success": False,
    "message": (
        "آدرس انتخاب‌شده معتبر نیست."
    ),
    "errors": None,
}


OrderNotFound = {
    "success": False,
    "message": (
        "سفارش موردنظر یافت نشد."
    ),
    "errors": None,
}


OrderCancelSuccess = {
    "success": True,
    "message": (
        "سفارش با موفقیت لغو شد."
    ),
    "data": {
        **OrderExample,
        "status": "cancelled",
    },
}

# =========================================================
# Order Cancellation Responses
# =========================================================


OrderCancellationSuccess = {
    "success": True,
    "message": "سفارش با موفقیت لغو شد.",
    "data": {
        "order_number": "RK-20260911-15E6223F",
        "order_status": "cancelled",
        "payment_status": "refunded",
        "already_cancelled": False,
        "shipment_id": 2,
        "shipment_status": "cancelled",
        "refund_public_id": (
            "3ed2af34-b77f-4bcd-81f9-0f37b0262047"
        ),
        "refund_status": "succeeded",
    },
}


OrderCancellationAlreadyCancelled = {
    "success": True,
    "message": "سفارش قبلاً لغو شده است.",
    "data": {
        "order_number": "RK-20260910-1C119582",
        "order_status": "cancelled",
        "payment_status": "refunded",
        "already_cancelled": True,
        "shipment_id": None,
        "shipment_status": None,
        "refund_public_id": (
            "414be19c-d0bc-4830-b965-acaee20adea2"
        ),
        "refund_status": "succeeded",
    },
}


OrderCancellationValidationError = {
    "success": False,
    "message": (
        "سفارش ارسال‌شده یا تحویل‌شده "
        "از مسیر Cancellation عادی قابل لغو نیست."
    ),
    "errors": None,
}


OrderCancellationReviewRequired = {
    "success": False,
    "message": (
        "نتیجه Refund/Reversal نامشخص است. "
        "Retry خودکار انجام نشود."
    ),
    "errors": {
        "review_required": True,
    },
}


OrderCancellationNotFound = {
    "success": False,
    "message": "سفارش موردنظر یافت نشد.",
    "errors": None,
}


OrderCancellationAuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    ),
}