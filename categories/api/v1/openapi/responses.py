# =========================================================
# Category List
# =========================================================


CategoryListAPIViewSuccess = {
    "success": True,
    "message": "لیست دسته‌بندی‌ها با موفقیت دریافت شد.",
    "count": 3,
    "data": [
        {
            "id": 1,
            "name": "قطعات موتور",
            "slug": "قطعات-موتور",
            "parent": None,
            "children": [
                2,
                3,
            ],
            "image": (
                "https://example.com/media/categories/"
                "category/2026/09/"
                "قطعات-موتور-a38c93f22018.webp"
            ),
            "description": (
                "انواع قطعات مرتبط با موتور "
                "و اجزای داخلی پیشرانه."
            ),
            "is_active": True,
            "created_at": "2026-09-01T10:30:00Z",
            "updated_at": "2026-09-01T10:30:00Z",
        },
        {
            "id": 2,
            "name": "سیلندر و پیستون",
            "slug": "سیلندر-و-پیستون",
            "parent": 1,
            "children": [],
            "image": None,
            "description": (
                "انواع سیلندر، پیستون و قطعات مرتبط."
            ),
            "is_active": True,
            "created_at": "2026-09-01T10:35:00Z",
            "updated_at": "2026-09-01T10:35:00Z",
        },
        {
            "id": 3,
            "name": "میل لنگ",
            "slug": "میل-لنگ",
            "parent": 1,
            "children": [],
            "image": None,
            "description": "انواع میل لنگ موتورسیکلت.",
            "is_active": True,
            "created_at": "2026-09-01T10:40:00Z",
            "updated_at": "2026-09-01T10:40:00Z",
        },
    ],
}


# =========================================================
# Category Detail
# =========================================================


CategoryDetailAPIViewSuccess = {
    "success": True,
    "message": "دسته‌بندی با موفقیت دریافت شد.",
    "data": {
        "id": 2,
        "name": "سیلندر و پیستون",
        "slug": "سیلندر-و-پیستون",
        "parent": {
            "id": 1,
            "name": "قطعات موتور",
            "slug": "قطعات-موتور",
        },
        "children": [
            {
                "id": 4,
                "name": "پیستون",
                "slug": "پیستون",
            },
            {
                "id": 5,
                "name": "رینگ پیستون",
                "slug": "رینگ-پیستون",
            },
        ],
        "image": None,
        "description": (
            "انواع سیلندر، پیستون و قطعات مرتبط."
        ),
        "is_active": True,
        "created_at": "2026-09-01T10:35:00Z",
        "updated_at": "2026-09-01T10:35:00Z",
    },
}


# =========================================================
# Category Create
# =========================================================


CategoryCreateAPIViewSuccess = {
    "success": True,
    "message": "دسته‌بندی با موفقیت ایجاد شد.",
    "data": {
        "id": 6,
        "name": "سیستم ترمز",
        "slug": "سیستم-ترمز",
        "parent": None,
        "children": [],
        "image": None,
        "description": (
            "لنت، دیسک و سایر قطعات مرتبط "
            "با سیستم ترمز موتورسیکلت."
        ),
        "is_active": True,
        "created_at": "2026-09-01T12:00:00Z",
        "updated_at": "2026-09-01T12:00:00Z",
    },
}


# =========================================================
# Category Update
# =========================================================


CategoryUpdateAPIViewSuccess = {
    "success": True,
    "message": "دسته‌بندی با موفقیت بروزرسانی شد.",
    "data": {
        "id": 6,
        "name": "قطعات سیستم ترمز",
        # Slug remains unchanged intentionally.
        "slug": "سیستم-ترمز",
        "parent": None,
        "children": [],
        "image": None,
        "description": (
            "انواع قطعات سیستم ترمز موتورسیکلت."
        ),
        "is_active": True,
        "created_at": "2026-09-01T12:00:00Z",
        "updated_at": "2026-09-01T12:15:00Z",
    },
}


# =========================================================
# Category Delete
# =========================================================


CategoryDeleteAPIViewSuccess = {
    "success": True,
    "message": "دسته‌بندی با موفقیت حذف شد.",
    "data": None,
}


CategoryDeleteProtected = {
    "success": False,
    "message": (
        "این دسته‌بندی به اطلاعات دیگری وابسته است "
        "و قابل حذف نیست."
    ),
    "errors": None,
}


# =========================================================
# Category Tree
# =========================================================


CategoryTreeAPIViewSuccess = {
    "success": True,
    "message": "ساختار دسته‌بندی‌ها با موفقیت دریافت شد.",
    "data": [
        {
            "id": 1,
            "name": "قطعات موتور",
            "slug": "قطعات-موتور",
            "image": (
                "https://example.com/media/categories/"
                "category/2026/09/"
                "قطعات-موتور-a38c93f22018.webp"
            ),
            "children": [
                {
                    "id": 2,
                    "name": "سیلندر و پیستون",
                    "slug": "سیلندر-و-پیستون",
                    "image": None,
                    "children": [
                        {
                            "id": 4,
                            "name": "پیستون",
                            "slug": "پیستون",
                            "image": None,
                            "children": [],
                        }
                    ],
                },
                {
                    "id": 3,
                    "name": "میل لنگ",
                    "slug": "میل-لنگ",
                    "image": None,
                    "children": [],
                },
            ],
        },
        {
            "id": 10,
            "name": "سیستم ترمز",
            "slug": "سیستم-ترمز",
            "image": None,
            "children": [
                {
                    "id": 11,
                    "name": "لنت ترمز",
                    "slug": "لنت-ترمز",
                    "image": None,
                    "children": [],
                }
            ],
        },
    ],
}


# =========================================================
# Validation Errors
# =========================================================


CategoryValidationError = {
    "name": [
        "این فیلد الزامی است.",
    ],
}


CategoryInvalidParent = {
    "parent": [
        "یک دسته‌بندی نمی‌تواند والد خودش باشد.",
    ],
}


CategoryCircularParent = {
    "parent": [
        "انتخاب این دسته والد باعث ایجاد حلقه می‌شود.",
    ],
}


CategoryInvalidImage = {
    "image": [
        "فرمت تصویر مجاز نیست. "
        "فرمت‌های مجاز: JPEG, JPG, PNG, WEBP"
    ],
}


# =========================================================
# Authentication / Permission
# =========================================================


CategoryAuthenticationRequired = {
    "detail": (
        "Authentication credentials were not provided."
    ),
}


CategoryPermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    ),
}


# =========================================================
# Not Found
# =========================================================


CategoryNotFound = {
    "detail": "No Category matches the given query.",
}