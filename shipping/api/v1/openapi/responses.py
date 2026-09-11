ShippingQuoteSuccess = {
    "success": True,
    "message": (
        "هزینه روش‌های ارسال "
        "با موفقیت محاسبه شد."
    ),
    "data": {
        "address_id": 12,
        "province": "تهران",
        "city": "تهران",
        "weight_grams": 2350,
        "quotes": [
            {
                "method": {
                    "id": 1,
                    "code": "post-pishtaz",
                    "name": "پست پیشتاز",
                    "provider": "post",
                    "service_code": "PISHTAZ",
                    "calculation_mode": "manual",
                    "description": "",
                    "estimated_min_days": 2,
                    "estimated_max_days": 5,
                    "is_active": True,
                    "sort_order": 1,
                },
                "amount_toman": 120000,
                "weight_grams": 2350,
                "is_available": True,
                "unavailable_reason": None,
            }
        ],
    },
}


ShippingInvalidAddress = {
    "success": False,
    "message": "آدرس ارسال معتبر نیست.",
    "errors": None,
}


ShippingMissingWeight = {
    "success": False,
    "message": (
        "وزن محصول «شمع NGK CPR6EA-9» "
        "تعریف نشده است."
    ),
    "errors": None,
}


ShippingRateUnavailable = {
    "success": True,
    "message": (
        "هزینه روش‌های ارسال "
        "با موفقیت محاسبه شد."
    ),
    "data": {
        "quotes": [
            {
                "method": {
                    "id": 1,
                    "code": "post-pishtaz",
                    "name": "پست پیشتاز",
                },
                "amount_toman": None,
                "weight_grams": 2500,
                "is_available": False,
                "unavailable_reason": (
                    "برای این روش ارسال، "
                    "مقصد و وزن تعرفه‌ای "
                    "تعریف نشده است."
                ),
            }
        ]
    },
}


AuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    )
}