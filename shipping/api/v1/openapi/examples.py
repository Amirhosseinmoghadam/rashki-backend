SHIPPING_METHOD_CREATE_EXAMPLE = {
    "code": "post-pishtaz",
    "name": "پست پیشتاز",
    "provider": "post",
    "service_code": "PISHTAZ",
    "calculation_mode": "manual",
    "description": (
        "ارسال با پست پیشتاز"
    ),
    "estimated_min_days": 2,
    "estimated_max_days": 5,
    "is_active": True,
    "sort_order": 1,
}


SHIPPING_RATE_CREATE_EXAMPLE = {
    "method_id": 1,
    "destination_scope": "nationwide",
    "province_id": None,
    "city_id": None,
    "min_weight_grams": 0,
    "max_weight_grams": 5000,
    "base_price_toman": 80000,
    "included_weight_grams": 1000,
    "additional_per_kg_toman": 20000,
    "priority": 0,
    "is_active": True,
    "note": "تعرفه عمومی پست",
}


SHIPPING_QUOTE_EXAMPLE = {
    "address_id": 12,
}