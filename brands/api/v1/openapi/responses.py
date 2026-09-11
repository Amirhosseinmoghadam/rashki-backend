# =========================================================
# Brand List
# =========================================================


BrandListAPIViewSuccess = {
    "success": True,
    "message": (
        "لیست برندها با موفقیت دریافت شد."
    ),
    "count": 3,
    "data": [
        {
            "id": 1,
            "name": "NGK",
            "slug": "ngk",
            "logo": (
                "https://example.com/media/"
                "brands/brand/2026/09/"
                "ngk-a38c93f22018.webp"
            ),
            "description": (
                "تولیدکننده شمع و قطعات "
                "سیستم احتراق موتورسیکلت."
            ),
        },
        {
            "id": 2,
            "name": "DID",
            "slug": "did",
            "logo": None,
            "description": (
                "تولیدکننده زنجیر و قطعات "
                "انتقال قدرت موتورسیکلت."
            ),
        },
        {
            "id": 3,
            "name": "BOSCH",
            "slug": "bosch",
            "logo": None,
            "description": (
                "تولیدکننده قطعات و تجهیزات "
                "سیستم‌های الکتریکی و احتراق."
            ),
        },
    ],
}


# =========================================================
# Brand Detail
# =========================================================


BrandDetailAPIViewSuccess = {
    "success": True,
    "message": (
        "برند با موفقیت دریافت شد."
    ),
    "data": {
        "id": 1,
        "name": "NGK",
        "slug": "ngk",
        "logo": (
            "https://example.com/media/"
            "brands/brand/2026/09/"
            "ngk-a38c93f22018.webp"
        ),
        "description": (
            "تولیدکننده شمع و قطعات "
            "سیستم احتراق موتورسیکلت."
        ),
        "website": "https://www.ngk.com/",
        "is_active": True,
        "created_at": (
            "2026-09-02T10:00:00Z"
        ),
        "updated_at": (
            "2026-09-02T10:00:00Z"
        ),
    },
}


# =========================================================
# Brand Create
# =========================================================


BrandCreateAPIViewSuccess = {
    "success": True,
    "message": (
        "برند با موفقیت ایجاد شد."
    ),
    "data": {
        "id": 4,
        "name": "DID",
        "slug": "did",
        "logo": None,
        "description": (
            "تولیدکننده زنجیر و قطعات "
            "انتقال قدرت موتورسیکلت."
        ),
        "website": (
            "https://www.didchain.com/"
        ),
        "is_active": True,
        "created_at": (
            "2026-09-02T12:00:00Z"
        ),
        "updated_at": (
            "2026-09-02T12:00:00Z"
        ),
    },
}


# =========================================================
# Brand Update
# =========================================================


BrandUpdateAPIViewSuccess = {
    "success": True,
    "message": (
        "برند با موفقیت بروزرسانی شد."
    ),
    "data": {
        "id": 4,
        "name": "DID",

        # Slug remains unchanged intentionally.
        "slug": "did",

        "logo": None,
        "description": (
            "تولیدکننده انواع زنجیر "
            "موتورسیکلت."
        ),
        "website": (
            "https://www.didchain.com/"
        ),
        "is_active": True,
        "created_at": (
            "2026-09-02T12:00:00Z"
        ),
        "updated_at": (
            "2026-09-02T12:30:00Z"
        ),
    },
}


# =========================================================
# Brand Delete
# =========================================================


BrandDeleteAPIViewSuccess = {
    "success": True,
    "message": (
        "برند با موفقیت حذف شد."
    ),
    "data": None,
}


BrandDeleteProtected = {
    "success": False,
    "message": (
        "این برند به اطلاعات دیگری "
        "وابسته است و قابل حذف نیست."
    ),
    "errors": None,
}


# =========================================================
# Validation Errors
# =========================================================


BrandValidationError = {
    "name": [
        "این فیلد الزامی است.",
    ],
}


BrandDuplicateName = {
    "name": [
        "برندی با این نام قبلاً ثبت شده است."
    ],
}


BrandInvalidImage = {
    "logo": [
        (
            "فرمت تصویر مجاز نیست. "
            "فرمت‌های مجاز: "
            "JPEG, JPG, PNG, WEBP"
        )
    ],
}


BrandInvalidWebsite = {
    "website": [
        "Enter a valid URL."
    ],
}


# =========================================================
# Authentication / Permission
# =========================================================


BrandAuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    ),
}


BrandPermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    ),
}


# =========================================================
# Not Found
# =========================================================


BrandNotFound = {
    "detail": (
        "No Brand matches the given query."
    ),
}