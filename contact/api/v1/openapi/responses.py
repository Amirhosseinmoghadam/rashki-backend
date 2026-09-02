# =========================================================
# Contact Create
# =========================================================


ContactCreateAPIViewSuccess = {
    "success": True,
    "message": (
        "درخواست شما با موفقیت ثبت شد."
    ),
    "data": {
        "id": 1,
    },
}


# =========================================================
# Contact Admin List
# =========================================================


ContactAdminListAPIViewSuccess = {
    "success": True,
    "message": (
        "لیست درخواست‌های تماس "
        "با موفقیت دریافت شد."
    ),
    "data": {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 1,
                "first_name": "امیرحسین",
                "last_name": "مقدم",
                "phone_number": "09196558273",
                "subject": "price_inquiry",
                "subject_display": "استعلام قیمت",
                "description": (
                    "سلام، لطفاً قیمت این "
                    "محصول را اعلام کنید."
                ),
                "is_read": False,
                "created_at": (
                    "2026-09-01T15:30:00Z"
                ),
                "updated_at": (
                    "2026-09-01T15:30:00Z"
                ),
            },
            {
                "id": 2,
                "first_name": "علی",
                "last_name": "رضایی",
                "phone_number": "09123456789",
                "subject": (
                    "wholesale_cooperation"
                ),
                "subject_display": (
                    "درخواست همکاری عمده"
                ),
                "description": (
                    "برای همکاری در زمینه "
                    "خرید عمده لوازم یدکی "
                    "موتورسیکلت تماس می‌گیرم."
                ),
                "is_read": True,
                "created_at": (
                    "2026-08-31T12:20:00Z"
                ),
                "updated_at": (
                    "2026-08-31T14:10:00Z"
                ),
            },
        ],
    },
}


# =========================================================
# Contact Admin Detail
# =========================================================


ContactAdminDetailAPIViewSuccess = {
    "success": True,
    "message": (
        "درخواست تماس با موفقیت دریافت شد."
    ),
    "data": {
        "id": 1,
        "first_name": "امیرحسین",
        "last_name": "مقدم",
        "phone_number": "09196558273",
        "subject": "price_inquiry",
        "subject_display": "استعلام قیمت",
        "description": (
            "سلام، لطفاً قیمت این محصول "
            "را اعلام کنید."
        ),
        "is_read": False,
        "created_at": (
            "2026-09-01T15:30:00Z"
        ),
        "updated_at": (
            "2026-09-01T15:30:00Z"
        ),
    },
}


# =========================================================
# Contact Admin Partial Update
# =========================================================


ContactAdminPartialUpdateAPIViewSuccess = {
    "success": True,
    "message": (
        "وضعیت درخواست تماس با موفقیت "
        "بروزرسانی شد."
    ),
    "data": {
        "id": 1,
        "first_name": "امیرحسین",
        "last_name": "مقدم",
        "phone_number": "09196558273",
        "subject": "price_inquiry",
        "subject_display": "استعلام قیمت",
        "description": (
            "سلام، لطفاً قیمت این محصول "
            "را اعلام کنید."
        ),
        "is_read": True,
        "created_at": (
            "2026-09-01T15:30:00Z"
        ),
        "updated_at": (
            "2026-09-01T15:40:00Z"
        ),
    },
}


# =========================================================
# Validation Errors
# =========================================================


ContactInvalidFirstName = {
    "first_name": [
        "وارد کردن نام الزامی است."
    ],
}


ContactInvalidLastName = {
    "last_name": [
        "وارد کردن نام خانوادگی الزامی است."
    ],
}


ContactInvalidPhoneNumber = {
    "phone_number": [
        "شماره تماس باید به صورت "
        "09123456789 باشد."
    ],
}


ContactInvalidSubject = {
    "subject": [
        "موضوع درخواست انتخاب‌شده معتبر نیست."
    ],
}


ContactInvalidDescription = {
    "description": [
        "توضیحات باید حداقل ۵ کاراکتر باشد."
    ],
}


ContactDuplicateRequest = {
    "non_field_errors": [
        (
            "این درخواست قبلاً ثبت شده است. "
            "لطفاً چند دقیقه بعد دوباره "
            "تلاش کنید."
        )
    ],
}


ContactInvalidReadStatus = {
    "is_read": [
        "Must be a valid boolean."
    ],
}


# =========================================================
# Authentication / Permission
# =========================================================


ContactAuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    ),
}


ContactPermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    ),
}


# =========================================================
# Not Found
# =========================================================


ContactNotFound = {
    "detail": (
        "درخواست تماس موردنظر پیدا نشد."
    ),
}


# =========================================================
# Rate Limit
# =========================================================


ContactRateLimitExceeded = {
    "detail": (
        "Request was throttled. "
        "Expected available in 3600 seconds."
    ),
}