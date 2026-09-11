DISCOUNT_PERCENTAGE_CREATE_EXAMPLE = {
    "code": "OFF20",
    "description": "کمپین تخفیف 20 درصدی",
    "discount_type": "percentage",
    "percentage": "20.00",
    "fixed_amount_toman": None,
    "minimum_order_toman": 1000000,
    "maximum_discount_toman": 300000,
    "scope": "all",
    "product_ids": [],
    "category_ids": [],
    "start_at": "2026-09-04T12:00:00Z",
    "end_at": "2026-10-04T12:00:00Z",
    "usage_limit": 1000,
    "usage_limit_per_user": 1,
    "is_active": True,
}


DISCOUNT_FIXED_CREATE_EXAMPLE = {
    "code": "WELCOME100",
    "description": "تخفیف خوش‌آمدگویی",
    "discount_type": "fixed_amount",
    "percentage": None,
    "fixed_amount_toman": 100000,
    "minimum_order_toman": 750000,
    "maximum_discount_toman": None,
    "scope": "all",
    "usage_limit": None,
    "usage_limit_per_user": 1,
    "is_active": True,
}


DISCOUNT_PRODUCT_SCOPE_EXAMPLE = {
    "code": "NGK15",
    "discount_type": "percentage",
    "percentage": "15.00",
    "minimum_order_toman": 500000,
    "maximum_discount_toman": 200000,
    "scope": "products",
    "product_ids": [
        25,
        28,
    ],
    "is_active": True,
}


DISCOUNT_VALIDATE_EXAMPLE = {
    "code": "OFF20",
    "items": [
        {
            "product_id": 25,
            "quantity": 2,
        },
        {
            "product_id": 28,
            "quantity": 1,
        },
    ],
}