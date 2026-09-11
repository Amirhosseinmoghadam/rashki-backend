# =========================================================
# Cart
# =========================================================


CartSuccess = {
    "success": True,
    "message": (
        "سبد خرید با موفقیت دریافت شد."
    ),
    "data": {
        "id": 8,
        "items": [
            {
                "id": 12,
                "product": {
                    "id": 25,
                    "name": "شمع NGK CPR6EA-9",
                    "slug": "شمع-ngk-cpr6ea-9",
                    "sku": "NGK-CPR6EA9",
                    "category": {
                        "id": 4,
                        "name": "شمع",
                        "slug": "شمع",
                    },
                    "brand": {
                        "id": 2,
                        "name": "NGK",
                        "slug": "ngk",
                        "logo": None,
                    },
                    "unit": "piece",
                    "primary_image": None,
                },
                "quantity": 2,
                "unit_price_toman": 590000,
                "line_total_toman": 1180000,
                "is_available": True,
                "availability_message": None,
                "available_stock": 30,
                "created_at": (
                    "2026-09-04T17:00:00Z"
                ),
                "updated_at": (
                    "2026-09-04T17:00:00Z"
                ),
            }
        ],
        "item_count": 1,
        "total_quantity": 2,
        "subtotal_toman": 1180000,
        "applied_discount": None,
        "discount_valid": None,
        "discount_error": None,
        "discount_amount_toman": 0,
        "final_subtotal_toman": 1180000,
        "has_issues": False,
        "is_checkout_ready": True,
        "created_at": (
            "2026-09-04T16:00:00Z"
        ),
        "updated_at": (
            "2026-09-04T17:00:00Z"
        ),
    },
}


# =========================================================
# Discount
# =========================================================


CartDiscountSuccess = {
    "success": True,
    "message": (
        "کد تخفیف با موفقیت "
        "روی سبد خرید اعمال شد."
    ),
    "data": {
        **CartSuccess["data"],
        "applied_discount": {
            "id": 4,
            "code": "OFF20",
            "discount_type": "percentage",
            "scope": "all",
            "eligible_subtotal_toman": 1180000,
            "discount_amount_toman": 236000,
        },
        "discount_valid": True,
        "discount_error": None,
        "discount_amount_toman": 236000,
        "final_subtotal_toman": 944000,
    },
}


# =========================================================
# Errors
# =========================================================


CartProductUnavailable = {
    "success": False,
    "message": (
        "محصول موردنظر در حال حاضر "
        "قابل خرید نیست."
    ),
    "errors": None,
}


CartStockError = {
    "success": False,
    "message": (
        "موجودی کافی نیست. "
        "موجودی فعلی 3 عدد است."
    ),
    "errors": None,
}


CartItemNotFound = {
    "success": False,
    "message": (
        "این محصول در سبد خرید "
        "وجود ندارد."
    ),
    "errors": None,
}


CartInvalidDiscount = {
    "success": False,
    "message": (
        "کد تخفیف معتبر نیست."
    ),
    "errors": None,
}


AuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    ),
}