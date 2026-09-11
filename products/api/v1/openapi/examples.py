# =========================================================
# Product Create - USD Based
# =========================================================


PRODUCT_CREATE_USD_EXAMPLE = {
    "name": "شمع NGK CPR6EA-9",
    "category": 4,
    "brand": 2,
    "unit": "piece",
    "sku": "NGK-CPR6EA9",
    "manufacturer_part_number": "CPR6EA-9",
    "oem_code": "",
    "barcode": None,
    "short_description": (
        "شمع NGK مناسب چند مدل موتورسیکلت هوندا."
    ),
    "description": (
        "شمع NGK مدل CPR6EA-9 با کیفیت بالا "
        "و مناسب استفاده در موتورهای سازگار."
    ),
    "search_keywords": (
        "شمع هوندا NGK CPR6EA9 هوندا 125"
    ),
    "pricing_mode": "usd_based",
    "base_price_usd": "4.5000",
    "base_price_toman": None,
    "markup_percent": "20.000",
    "fixed_cost_toman": 20000,
    "is_price_locked": False,
    "stock_quantity": 30,
    "low_stock_threshold": 3,
    "weight_grams": 80,
    "length_cm": "8.00",
    "width_cm": "3.00",
    "height_cm": "3.00",
    "meta_title": "خرید شمع NGK CPR6EA-9",
    "meta_description": (
        "خرید شمع NGK CPR6EA-9 مناسب "
        "موتورسیکلت‌های سازگار."
    ),
    "status": "active",
    "is_featured": False,
    "attributes": [
        {
            "attribute": 5,
            "value_number": "10.0000",
        },
        {
            "attribute": 6,
            "option": 14,
        },
    ],
    "compatibilities": [
        {
            "motorcycle": 2,
            "compatible_start_year": 2018,
            "compatible_end_year": None,
            "note": "",
        },
        {
            "motorcycle": 4,
            "compatible_start_year": None,
            "compatible_end_year": None,
            "note": "",
        },
    ],
    "related_product_ids": [18, 20],
}


# =========================================================
# Product Create - Fixed Toman
# =========================================================


PRODUCT_CREATE_FIXED_EXAMPLE = {
    "name": "لنت ترمز جلو",
    "category": 7,
    "brand": None,
    "unit": "pair",
    "sku": "BRK-FRONT-001",
    "manufacturer_part_number": "",
    "oem_code": "",
    "short_description": "لنت ترمز جلو موتورسیکلت.",
    "pricing_mode": "fixed",
    "base_price_usd": None,
    "base_price_toman": 450000,
    "markup_percent": "10.000",
    "fixed_cost_toman": 15000,
    "is_price_locked": False,
    "stock_quantity": 15,
    "low_stock_threshold": 3,
    "weight_grams": 320,
    "status": "draft",
    "is_featured": False,
    "attributes": [],
    "compatibilities": [],
    "related_product_ids": [],
}


# =========================================================
# Product Update
# =========================================================


PRODUCT_UPDATE_EXAMPLE = {
    "name": "شمع NGK CPR6EA-9",
    "category": 4,
    "brand": 2,
    "unit": "piece",
    "sku": "NGK-CPR6EA9",
    "manufacturer_part_number": "CPR6EA-9",
    "oem_code": "",
    "barcode": None,
    "short_description": (
        "شمع NGK مناسب موتورسیکلت‌های هوندا."
    ),
    "description": (
        "نسخه بروزرسانی‌شده توضیحات محصول."
    ),
    "search_keywords": "NGK CPR6EA9 شمع هوندا",
    "pricing_mode": "usd_based",
    "base_price_usd": "4.7500",
    "base_price_toman": None,
    "markup_percent": "20.000",
    "fixed_cost_toman": 20000,
    "is_price_locked": False,
    "stock_quantity": 25,
    "low_stock_threshold": 3,
    "weight_grams": 80,
    "length_cm": "8.00",
    "width_cm": "3.00",
    "height_cm": "3.00",
    "meta_title": "شمع NGK CPR6EA-9",
    "meta_description": "شمع NGK مناسب موتورهای سازگار.",
    "status": "active",
    "is_featured": True,
    "attributes": [
        {
            "attribute": 5,
            "value_number": "10.0000",
        }
    ],
    "compatibilities": [
        {
            "motorcycle": 2,
            "compatible_start_year": 2018,
            "compatible_end_year": None,
            "note": "",
        }
    ],
    "related_product_ids": [18],
}


# =========================================================
# Product Partial Update
# =========================================================


PRODUCT_PARTIAL_UPDATE_EXAMPLE = {
    "stock_quantity": 20,
    "is_featured": True,
}


# =========================================================
# Product Image
# =========================================================


PRODUCT_IMAGE_CREATE_EXAMPLE = {
    "product": 25,
    "image": "<binary-file>",
    "alt_text": "نمای اصلی شمع NGK CPR6EA-9",
    "is_primary": True,
    "sort_order": 0,
}


PRODUCT_IMAGE_UPDATE_EXAMPLE = {
    "product": 25,
    "image": "<binary-file>",
    "alt_text": "نمای جدید شمع NGK CPR6EA-9",
    "is_primary": True,
    "sort_order": 0,
}


PRODUCT_IMAGE_PARTIAL_UPDATE_EXAMPLE = {
    "alt_text": "نمای بسته‌بندی محصول",
    "sort_order": 2,
}