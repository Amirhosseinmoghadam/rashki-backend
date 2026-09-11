# =========================================================
# Product List
# =========================================================


ProductListSuccess = {
    "success": True,
    "message": "لیست محصولات با موفقیت دریافت شد.",
    "data": {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
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
                "short_description": (
                    "شمع NGK مناسب چند مدل "
                    "موتورسیکلت هوندا."
                ),
                "current_price_toman": 590000,
                "unit": "piece",
                "stock_quantity": 30,
                "is_in_stock": True,
                "is_featured": False,
                "primary_image": (
                    "http://127.0.0.1:8000/"
                    "media/products/product/2026/09/"
                    "ngk-main.png"
                ),
            },
            {
                "id": 26,
                "name": "لنت ترمز جلو",
                "slug": "لنت-ترمز-جلو",
                "sku": "BRK-FRONT-001",
                "category": {
                    "id": 7,
                    "name": "لنت ترمز",
                    "slug": "لنت-ترمز",
                },
                "brand": None,
                "short_description": (
                    "لنت ترمز جلو موتورسیکلت."
                ),
                "current_price_toman": 510000,
                "unit": "pair",
                "stock_quantity": 15,
                "is_in_stock": True,
                "is_featured": False,
                "primary_image": None,
            },
        ],
    },
}


# =========================================================
# Product Detail
# =========================================================


ProductDetailSuccess = {
    "success": True,
    "message": "محصول با موفقیت دریافت شد.",
    "data": {
        "id": 25,
        "name": "شمع NGK CPR6EA-9",
        "slug": "شمع-ngk-cpr6ea-9",
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
        "sku": "NGK-CPR6EA9",
        "manufacturer_part_number": "CPR6EA-9",
        "oem_code": "",
        "barcode": None,
        "short_description": (
            "شمع NGK مناسب چند مدل موتورسیکلت هوندا."
        ),
        "description": (
            "شمع NGK مدل CPR6EA-9 با کیفیت بالا."
        ),
        "current_price_toman": 590000,
        "stock_quantity": 30,
        "is_in_stock": True,
        "weight_grams": 80,
        "length_cm": "8.00",
        "width_cm": "3.00",
        "height_cm": "3.00",
        "images": [
            {
                "id": 10,
                "image": (
                    "http://127.0.0.1:8000/"
                    "media/products/product/2026/09/"
                    "ngk-main.png"
                ),
                "alt_text": "شمع NGK CPR6EA-9",
                "is_primary": True,
                "sort_order": 0,
            }
        ],
        "attributes": [
            {
                "id": 1,
                "attribute": {
                    "id": 5,
                    "name": "قطر رزوه",
                    "slug": "قطر-رزوه",
                    "data_type": "number",
                    "unit": "mm",
                    "is_filterable": True,
                    "is_searchable": False,
                    "sort_order": 0,
                    "options": [],
                },
                "value_text": "",
                "value_number": "10.0000",
                "value_boolean": None,
                "option": None,
            }
        ],
        "compatibilities": [
            {
                "id": 1,
                "motorcycle": {
                    "id": 2,
                    "brand": {
                        "id": 1,
                        "name": "هوندا",
                        "slug": "هوندا",
                    },
                    "name": "CG 125",
                    "slug": "هوندا-cg-125",
                    "engine_volume": 125,
                    "production_start_year": 2010,
                    "production_end_year": None,
                },
                "compatible_start_year": 2018,
                "compatible_end_year": None,
                "note": "",
            }
        ],
        "related_products": [
            {
                "id": 18,
                "name": "وایر شمع",
                "slug": "وایر-شمع",
                "current_price_toman": 180000,
                "primary_image": None,
            }
        ],
        "meta_title": "خرید شمع NGK CPR6EA-9",
        "meta_description": (
            "خرید شمع NGK مناسب موتورسیکلت‌های سازگار."
        ),
        "is_featured": False,
        "created_at": "2026-09-04T10:00:00Z",
        "updated_at": "2026-09-04T10:00:00Z",
    },
}


# =========================================================
# Product Create
# =========================================================


ProductCreateSuccess = {
    "success": True,
    "message": "محصول با موفقیت ایجاد شد.",
    "data": ProductDetailSuccess["data"],
}


# =========================================================
# Product Update
# =========================================================


ProductUpdateSuccess = {
    "success": True,
    "message": "محصول با موفقیت بروزرسانی شد.",
    "data": ProductDetailSuccess["data"],
}


# =========================================================
# Product Delete
# =========================================================


ProductDeleteSuccess = {
    "success": True,
    "message": "محصول با موفقیت حذف شد.",
    "data": None,
}


ProductDeleteProtected = {
    "success": False,
    "message": (
        "این محصول به اطلاعات دیگری وابسته است "
        "و قابل حذف نیست."
    ),
    "errors": None,
}


# =========================================================
# Validation Errors
# =========================================================


ProductValidationError = {
    "name": [
        "این فیلد الزامی است."
    ]
}


ProductUSDPriceRequired = {
    "base_price_usd": [
        (
            "برای قیمت‌گذاری دلاری "
            "قیمت پایه دلار الزامی است."
        )
    ]
}


ProductTomanPriceRequired = {
    "base_price_toman": [
        (
            "برای قیمت‌گذاری ثابت "
            "قیمت پایه تومان الزامی است."
        )
    ]
}


ProductInactiveCategory = {
    "category": [
        (
            "محصول فعال باید در دسته‌بندی فعال "
            "قرار گیرد و تمام والدهای دسته‌بندی "
            "نیز فعال باشند."
        )
    ]
}


ProductInactiveBrand = {
    "brand": [
        (
            "برند محصول فعال نمی‌تواند "
            "غیرفعال باشد."
        )
    ]
}


ProductInvalidAttribute = {
    "attributes": [
        (
            "یک یا چند ویژگی برای دسته‌بندی "
            "این محصول تعریف نشده‌اند."
        )
    ]
}


ProductMissingRequiredAttribute = {
    "attributes": [
        (
            "برخی ویژگی‌های الزامی این "
            "دسته‌بندی وارد نشده‌اند."
        )
    ]
}


ProductDuplicateCompatibility = {
    "compatibilities": [
        (
            "یک مدل موتورسیکلت بیش از "
            "یک بار ارسال شده است."
        )
    ]
}


ProductPricingError = {
    "pricing": (
        "نرخ فعال برای ارز USD تعریف نشده است."
    )
}


# =========================================================
# Product Not Found
# =========================================================


ProductNotFound = {
    "detail": (
        "No Product matches the given query."
    )
}


# =========================================================
# Authentication / Permission
# =========================================================


AuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    )
}


PermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    )
}


# =========================================================
# Product Image
# =========================================================


ProductImageSuccess = {
    "id": 10,
    "image": (
        "http://127.0.0.1:8000/"
        "media/products/product/2026/09/"
        "ngk-main.png"
    ),
    "alt_text": "نمای اصلی شمع NGK CPR6EA-9",
    "is_primary": True,
    "sort_order": 0,
}


ProductImageListSuccess = [
    ProductImageSuccess,
    {
        "id": 11,
        "image": (
            "http://127.0.0.1:8000/"
            "media/products/product/2026/09/"
            "ngk-package.png"
        ),
        "alt_text": "بسته‌بندی محصول",
        "is_primary": False,
        "sort_order": 1,
    },
]


ProductImageLimitError = {
    "image": [
        (
            "برای هر محصول حداکثر "
            "20 تصویر قابل ثبت است."
        )
    ]
}


ProductImageMoveError = {
    "product": [
        (
            "انتقال تصویر از یک محصول "
            "به محصول دیگر مجاز نیست."
        )
    ]
}


# =========================================================
# Attribute
# =========================================================


ProductAttributeListSuccess = [
    {
        "id": 5,
        "name": "قطر رزوه",
        "slug": "قطر-رزوه",
        "data_type": "number",
        "unit": "mm",
        "is_filterable": True,
        "is_searchable": False,
        "sort_order": 0,
        "options": [],
    },
    {
        "id": 6,
        "name": "محل نصب",
        "slug": "محل-نصب",
        "data_type": "choice",
        "unit": "",
        "is_filterable": True,
        "is_searchable": False,
        "sort_order": 1,
        "options": [
            {
                "id": 14,
                "value": "جلو",
                "slug": "جلو",
                "sort_order": 0,
            },
            {
                "id": 15,
                "value": "عقب",
                "slug": "عقب",
                "sort_order": 1,
            },
        ],
    },
]