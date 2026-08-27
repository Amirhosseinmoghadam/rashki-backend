# =========================================================
# Cart API Examples
# =========================================================

CartListViewExample = {}

AddToCartViewExample = {
    "variant_id": 1,
    "quantity": 2,
}

UpdateCartItemViewExample = {
    "quantity": 5,
}

RemoveCartItemViewExample = {}

ClearCartViewExample = {}


# =========================================================
# Cart API Responses
# =========================================================

CartListViewSuccess = {
    "message": "سبد خرید با موفقیت دریافت شد.",
    "data": {
        "id": 1,
        "user": 1,
        "items": [
            {
                "id": 1,
                "cart": 1,
                "variant": 1,
                "variant_id": 1,
                "variant_name": "CG125 - جلو - مشکی",
                "variant_sku": "CG125-F-BLK",
                "variant_price": "1500000",
                "variant_is_active": True,
                "quantity": 2,
                "total_price": "3000000",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            }
        ],
        "total_items": 1,
        "subtotal": "3000000",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    },
}

AddToCartViewSuccess = {
    "message": "محصول با موفقیت به سبد خرید اضافه شد.",
    "data": {
        "id": 1,
        "user": 1,
        "items": [
            {
                "id": 1,
                "cart": 1,
                "variant": 1,
                "variant_id": 1,
                "variant_name": "CG125 - جلو - مشکی",
                "variant_sku": "CG125-F-BLK",
                "variant_price": "1500000",
                "variant_is_active": True,
                "quantity": 2,
                "total_price": "3000000",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            }
        ],
        "total_items": 1,
        "subtotal": "3000000",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    },
}

UpdateCartItemViewSuccess = {
    "message": "تعداد محصول با موفقیت بروزرسانی شد.",
    "data": {
        "id": 1,
        "user": 1,
        "items": [
            {
                "id": 1,
                "cart": 1,
                "variant": 1,
                "variant_id": 1,
                "variant_name": "CG125 - جلو - مشکی",
                "variant_sku": "CG125-F-BLK",
                "variant_price": "1500000",
                "variant_is_active": True,
                "quantity": 5,
                "total_price": "7500000",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
            }
        ],
        "total_items": 1,
        "subtotal": "7500000",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    },
}

RemoveCartItemViewSuccess = {
    "message": "محصول با موفقیت از سبد خرید حذف شد.",
    "data": {
        "id": 1,
        "user": 1,
        "items": [],
        "total_items": 0,
        "subtotal": 0,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    },
}

ClearCartViewSuccess = {
    "message": "سبد خرید با موفقیت خالی شد.",
    "data": {
        "id": 1,
        "user": 1,
        "items": [],
        "total_items": 0,
        "subtotal": 0,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
    },
}

ValidationError = {
    "detail": "وارد کردن این فیلد الزامی است.",
}

NotFoundError = {
    "detail": "یافت نشد.",
}
