# =========================================================
# Contact Create
# =========================================================

ContactCreateAPIViewSuccess = {
    "message": "درخواست شما با موفقیت ثبت شد.",
    "data": {
        "id": 1,
    },
}


# =========================================================
# Contact Admin List
# =========================================================

ContactAdminListAPIViewSuccess = {
    "count": 2,
    "results": [
        {
            "id": 1,
            "first_name": "امیرحسین",
            "last_name": "مقدم",
            "phone_number": "09196558273",
            "subject": "price_inquiry",
            "subject_display": "استعلام قیمت",
            "description": (
                "سلام، لطفاً قیمت این محصول را اعلام کنید."
            ),
            "is_read": False,
            "created_at": "2026-08-19T15:30:00Z",
            "updated_at": "2026-08-19T15:30:00Z",
        },
        {
            "id": 2,
            "first_name": "علی",
            "last_name": "رضایی",
            "phone_number": "09123456789",
            "subject": "wholesale_cooperation",
            "subject_display": "درخواست همکاری عمده",
            "description": (
                "برای همکاری در زمینه خرید عمده "
                "لوازم یدکی موتور سیکلت تماس می‌گیرم."
            ),
            "is_read": True,
            "created_at": "2026-08-18T12:20:00Z",
            "updated_at": "2026-08-18T14:10:00Z",
        },
    ],
}


# =========================================================
# Contact Admin Detail
# =========================================================

ContactAdminDetailAPIViewSuccess = {
    "id": 1,
    "first_name": "امیرحسین",
    "last_name": "مقدم",
    "phone_number": "09196558273",
    "subject": "price_inquiry",
    "subject_display": "استعلام قیمت",
    "description": (
        "سلام، لطفاً قیمت این محصول را اعلام کنید."
    ),
    "is_read": False,
    "created_at": "2026-08-19T15:30:00Z",
    "updated_at": "2026-08-19T15:30:00Z",
}


# =========================================================
# Contact Admin Partial Update
# =========================================================

ContactAdminPartialUpdateAPIViewSuccess = {
    "id": 1,
    "first_name": "امیرحسین",
    "last_name": "مقدم",
    "phone_number": "09196558273",
    "subject": "price_inquiry",
    "subject_display": "استعلام قیمت",
    "description": (
        "سلام، لطفاً قیمت این محصول را اعلام کنید."
    ),
    "is_read": True,
    "created_at": "2026-08-19T15:30:00Z",
    "updated_at": "2026-08-19T15:40:00Z",
}


# =========================================================
# Common Errors
# =========================================================

ContactValidationError = {
    "phone_number": [
        "شماره تماس باید به صورت 09123456789 باشد."
    ],
}


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
        "شماره تماس باید به صورت 09123456789 باشد."
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
            "لطفاً چند دقیقه بعد دوباره تلاش کنید."
        )
    ],
}


ContactAuthenticationRequired = {
    "detail": "Authentication credentials were not provided."
}


ContactPermissionDenied = {
    "detail": "You do not have permission to perform this action."
}


ContactNotFound = {
    "detail": "درخواست تماس موردنظر پیدا نشد."
}


ContactRateLimitExceeded = {
    "detail": (
        "Request was throttled. "
        "Expected available in 60 seconds."
    ),
}