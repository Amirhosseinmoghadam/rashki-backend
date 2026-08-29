# =========================================================
# Product Responses
# =========================================================

ProductListSuccess = {
    "count": 10,
    "results": [
        {
            "id": 1,
            "name": "لنت ترمز جلو CG125",
            "slug": "cg125-front-brake-pad",
            "brand": 1,
            "brand_name": "کاسه‌ای",
            "category": 1,
            "category_name": "لنت ترمز",
            "short_description": "لنت ترمز با کیفیت بالا برای CG125",
            "is_active": True,
            "is_featured": True,
            "created_at": "2024-01-15T10:30:00Z",
            "primary_image": {
                "id": 1,
                "image_url": "/media/products/images/brake_pad.jpg",
                "alt_text": "لنت ترمز CG125",
            },
            "variants_count": 3,
        }
    ],
}


ProductDetailSuccess = {
    "id": 1,
    "name": "لنت ترمز جلو CG125",
    "slug": "cg125-front-brake-pad",
    "brand": 1,
    "brand_name": "کاسه‌ای",
    "category": 1,
    "category_name": "لنت ترمز",
    "short_description": "لنت ترمز با کیفیت بالا برای CG125",
    "description": "این لنت ترمز با استفاده از مواد اولیه درجه یک تولید شده و عمر مفید بالایی دارد.",
    "is_active": True,
    "is_featured": True,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z",
    "images": [],
    "attribute_values": [],
    "variants": [],
    "motorcycle_compatibilities": [],
}


ProductCreateSuccess = {
    "message": "محصول با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "name": "لنت ترمز جلو CG125",
        "brand": 1,
        "category": 1,
        "short_description": "لنت ترمز با کیفیت بالا برای CG125",
        "description": "",
        "is_active": True,
        "is_featured": False,
    },
}


ProductUpdateSuccess = {
    "message": "محصول با موفقیت بروزرسانی شد.",
    "data": {
        "id": 1,
        "name": "لنت ترمز جلو CG125 - نسخه جدید",
        "brand": 1,
        "category": 1,
        "short_description": "لنت ترمز با کیفیت بالا برای CG125",
        "description": "",
        "is_active": True,
        "is_featured": True,
    },
}


ProductDeleteSuccess = {
    "message": "محصول با موفقیت حذف شد.",
}


ProductNotFoundError = {
    "detail": "Not found.",
}


ProductValidationError = {
    "message": "خطا در ایجاد محصول.",
    "errors": {
        "name": ["این فیلد الزامی است."],
        "brand": ["این فیلد الزامی است."],
        "category": ["این فیلد الزامی است."],
    },
}


# =========================================================
# Product Image Responses
# =========================================================

ProductImageCreateSuccess = {
    "message": "تصویر محصول با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "product": 1,
        "image": "/media/products/images/brake_pad.jpg",
        "alt_text": "لنت ترمز CG125",
        "caption": "تصویر اصلی",
        "is_primary": True,
        "sort_order": 0,
        "created_at": "2024-01-15T10:30:00Z",
    },
}


ProductImageDeleteSuccess = {
    "message": "تصویر محصول با موفقیت حذف شد.",
}


# =========================================================
# Attribute Group Responses
# =========================================================

AttributeGroupListSuccess = [
    {
        "id": 1,
        "name": "مشخصات فنی",
        "slug": "technical-specs",
        "sort_order": 0,
        "is_active": True,
    }
]


AttributeGroupCreateSuccess = {
    "message": "گروه ویژگی با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "name": "مشخصات فنی",
        "slug": "technical-specs",
        "sort_order": 0,
        "is_active": True,
    },
}


AttributeGroupDeleteSuccess = {
    "message": "گروه ویژگی با موفقیت حذف شد.",
}


# =========================================================
# Attribute Responses
# =========================================================

AttributeListSuccess = [
    {
        "id": 1,
        "group": 1,
        "group_name": "مشخصات فنی",
        "name": "جنس",
        "slug": "material",
        "value_type": "text",
        "value_type_display": "متن",
        "unit": "",
        "is_filterable": True,
        "is_required": False,
        "sort_order": 0,
        "is_active": True,
    }
]


AttributeCreateSuccess = {
    "message": "ویژگی با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "group": 1,
        "name": "جنس",
        "slug": "material",
        "value_type": "text",
        "unit": "",
        "is_filterable": True,
        "is_required": False,
        "sort_order": 0,
        "is_active": True,
    },
}


AttributeDeleteSuccess = {
    "message": "ویژگی با موفقیت حذف شد.",
}


# =========================================================
# Attribute Value Responses
# =========================================================

AttributeValueCreateSuccess = {
    "message": "مقدار ویژگی با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "attribute": 1,
        "value": "سرامیک",
        "slug": "ceramic",
        "sort_order": 0,
        "is_active": True,
    },
}


AttributeValueDeleteSuccess = {
    "message": "مقدار ویژگی با موفقیت حذف شد.",
}


# =========================================================
# Product Variant Responses
# =========================================================

ProductVariantListSuccess = [
    {
        "id": 1,
        "product": 1,
        "name": "مدل استاندارد",
        "sku": "CG125-BP-STD",
        "price": "150000",
        "stock": 50,
        "is_active": True,
        "is_in_stock": True,
        "is_available": True,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:45:00Z",
    }
]


ProductVariantCreateSuccess = {
    "message": "تنوع محصول با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "product": 1,
        "name": "مدل استاندارد",
        "sku": "CG125-BP-STD",
        "price": "150000",
        "stock": 50,
        "is_active": True,
    },
}


ProductVariantDeleteSuccess = {
    "message": "تنوع محصول با موفقیت حذف شد.",
}


# =========================================================
# Product Motorcycle Compatibility Responses
# =========================================================

ProductMotorcycleCompatibilityCreateSuccess = {
    "message": "سازگاری موتورسیکلت با موفقیت ایجاد شد.",
    "data": {
        "id": 1,
        "product": 1,
        "motorcycle": 1,
        "motorcycle_name": "CG125",
        "note": "سازگار با تمام مدل‌های CG125",
    },
}


ProductMotorcycleCompatibilityDeleteSuccess = {
    "message": "سازگاری موتورسیکلت با موفقیت حذف شد.",
}
