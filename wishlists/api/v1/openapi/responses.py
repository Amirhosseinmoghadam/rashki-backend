# =========================================================
# Wishlist Item
# =========================================================


WishlistItemExample = {
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
        "short_description": (
            "شمع NGK مناسب چند مدل "
            "موتورسیکلت هوندا."
        ),
        "current_price_toman": 590000,
        "unit": "piece",
        "stock_quantity": 30,
        "is_in_stock": True,
        "primary_image": (
            "http://127.0.0.1:8000/"
            "media/products/product/2026/09/"
            "ngk-main.png"
        ),
    },
    "created_at": (
        "2026-09-04T17:00:00Z"
    ),
}


# =========================================================
# List
# =========================================================


WishlistListSuccess = {
    "success": True,
    "message": (
        "لیست علاقه‌مندی‌ها "
        "با موفقیت دریافت شد."
    ),
    "data": {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            WishlistItemExample,
        ],
    },
}


# =========================================================
# Add
# =========================================================


WishlistAddSuccess = {
    "success": True,
    "message": (
        "محصول با موفقیت به "
        "علاقه‌مندی‌ها اضافه شد."
    ),
    "data": WishlistItemExample,
}


WishlistAlreadyExists = {
    "success": True,
    "message": (
        "این محصول از قبل در "
        "علاقه‌مندی‌های شما وجود دارد."
    ),
    "data": WishlistItemExample,
}


# =========================================================
# Remove
# =========================================================


WishlistRemoveSuccess = {
    "success": True,
    "message": (
        "محصول با موفقیت از "
        "علاقه‌مندی‌ها حذف شد."
    ),
    "data": None,
}


# =========================================================
# Product IDs
# =========================================================


WishlistProductIdsSuccess = {
    "success": True,
    "message": (
        "شناسه محصولات مورد علاقه "
        "با موفقیت دریافت شد."
    ),
    "count": 3,
    "data": [
        2,
        8,
        25,
    ],
}


# =========================================================
# Errors
# =========================================================


WishlistProductNotFound = {
    "success": False,
    "message": (
        "محصول موردنظر یافت نشد "
        "یا در حال حاضر قابل نمایش نیست."
    ),
    "errors": None,
}


WishlistItemNotFound = {
    "success": False,
    "message": (
        "این محصول در علاقه‌مندی‌های "
        "شما وجود ندارد."
    ),
    "errors": None,
}


AuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    )
}