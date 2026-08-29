# =========================================================
# Product Examples
# =========================================================

ProductListExample = {
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


ProductDetailExample = {
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
    "images": [
        {
            "id": 1,
            "product": 1,
            "image": "/media/products/images/brake_pad.jpg",
            "alt_text": "لنت ترمز CG125",
            "caption": "تصویر اصلی",
            "is_primary": True,
            "sort_order": 0,
            "created_at": "2024-01-15T10:30:00Z",
        }
    ],
    "attribute_values": [
        {
            "id": 1,
            "product": 1,
            "attribute": 1,
            "attribute_name": "جنس",
            "attribute_slug": "material",
            "value": "سرامیک",
        }
    ],
    "variants": [
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
    ],
    "motorcycle_compatibilities": [
        {
            "id": 1,
            "product": 1,
            "motorcycle": 1,
            "motorcycle_name": "CG125",
            "note": "",
        }
    ],
}


ProductCreateExample = {
    "name": "لنت ترمز جلو CG125",
    "brand": 1,
    "category": 1,
    "short_description": "لنت ترمز با کیفیت بالا برای CG125",
    "description": "این لنت ترمز با استفاده از مواد اولیه درجه یک تولید شده است.",
    "is_active": True,
    "is_featured": False,
}


# =========================================================
# Product Image Examples
# =========================================================

ProductImageCreateExample = {
    "product": 1,
    "image": "products/images/brake_pad.jpg",
    "alt_text": "لنت ترمز CG125",
    "caption": "تصویر اصلی محصول",
    "is_primary": True,
    "sort_order": 0,
}


# =========================================================
# Attribute Group Examples
# =========================================================

AttributeGroupListExample = [
    {
        "id": 1,
        "name": "مشخصات فنی",
        "slug": "technical-specs",
        "sort_order": 0,
        "is_active": True,
    }
]


AttributeGroupCreateExample = {
    "name": "مشخصات فنی",
    "sort_order": 0,
    "is_active": True,
}


# =========================================================
# Attribute Examples
# =========================================================

AttributeListExample = [
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


AttributeCreateExample = {
    "group": 1,
    "name": "جنس",
    "value_type": "text",
    "unit": "",
    "is_filterable": True,
    "is_required": False,
    "sort_order": 0,
    "is_active": True,
}


# =========================================================
# Attribute Value Examples
# =========================================================

AttributeValueListExample = [
    {
        "id": 1,
        "attribute": 1,
        "attribute_name": "جنس",
        "value": "سرامیک",
        "slug": "ceramic",
        "sort_order": 0,
        "is_active": True,
    }
]


AttributeValueCreateExample = {
    "attribute": 1,
    "value": "سرامیک",
    "sort_order": 0,
    "is_active": True,
}


# =========================================================
# Product Variant Examples
# =========================================================

ProductVariantListExample = [
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


ProductVariantCreateExample = {
    "product": 1,
    "name": "مدل استاندارد",
    "sku": "CG125-BP-STD",
    "price": "150000",
    "stock": 50,
    "is_active": True,
}


# =========================================================
# Product Motorcycle Compatibility Examples
# =========================================================

ProductMotorcycleCompatibilityCreateExample = {
    "product": 1,
    "motorcycle": 1,
    "note": "سازگار با تمام مدل‌های CG125",
}
