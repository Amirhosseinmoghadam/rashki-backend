# =========================================================
# Motorcycle Brand List
# =========================================================


MotorcycleBrandListSuccess = {
    "success": True,
    "message": (
        "لیست برندهای موتورسیکلت "
        "با موفقیت دریافت شد."
    ),
    "count": 2,
    "data": [
        {
            "id": 1,
            "name": "هوندا",
            "slug": "هوندا",
            "logo": None,
        },
        {
            "id": 2,
            "name": "TVS",
            "slug": "tvs",
            "logo": None,
        },
    ],
}


# =========================================================
# Motorcycle Brand Detail
# =========================================================


MotorcycleBrandDetailSuccess = {
    "success": True,
    "message": (
        "برند موتورسیکلت "
        "با موفقیت دریافت شد."
    ),
    "data": {
        "id": 1,
        "name": "هوندا",
        "slug": "هوندا",
        "logo": None,
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
# Motorcycle Brand Create
# =========================================================


MotorcycleBrandCreateSuccess = {
    "success": True,
    "message": (
        "برند موتورسیکلت "
        "با موفقیت ایجاد شد."
    ),
    "data": (
        MotorcycleBrandDetailSuccess[
            "data"
        ]
    ),
}


# =========================================================
# Motorcycle Brand Update
# =========================================================


MotorcycleBrandUpdateSuccess = {
    "success": True,
    "message": (
        "برند موتورسیکلت "
        "با موفقیت بروزرسانی شد."
    ),
    "data": (
        MotorcycleBrandDetailSuccess[
            "data"
        ]
    ),
}


# =========================================================
# Motorcycle Brand Delete
# =========================================================


MotorcycleBrandDeleteSuccess = {
    "success": True,
    "message": (
        "برند موتورسیکلت "
        "با موفقیت حذف شد."
    ),
    "data": None,
}


MotorcycleBrandDeleteProtected = {
    "success": False,
    "message": (
        "این برند دارای مدل یا "
        "اطلاعات وابسته است "
        "و قابل حذف نیست."
    ),
    "errors": None,
}


# =========================================================
# Motorcycle Model List
# =========================================================


MotorcycleModelListSuccess = {
    "success": True,
    "message": (
        "لیست موتورسیکلت‌ها "
        "با موفقیت دریافت شد."
    ),
    "count": 2,
    "data": [
        {
            "id": 1,
            "brand": {
                "id": 1,
                "name": "هوندا",
                "slug": "هوندا",
            },
            "name": "CG 125",
            "slug": "هوندا-cg-125",
            "production_start_year": 2010,
            "production_end_year": None,
            "engine_volume": 125,
            "image": None,
        },
        {
            "id": 2,
            "brand": {
                "id": 1,
                "name": "هوندا",
                "slug": "هوندا",
            },
            "name": "Click 150",
            "slug": "هوندا-click-150",
            "production_start_year": 2018,
            "production_end_year": None,
            "engine_volume": 150,
            "image": None,
        },
    ],
}


# =========================================================
# Motorcycle Model Detail
# =========================================================


MotorcycleModelDetailSuccess = {
    "success": True,
    "message": (
        "موتورسیکلت با موفقیت "
        "دریافت شد."
    ),
    "data": {
        "id": 1,
        "brand": {
            "id": 1,
            "name": "هوندا",
            "slug": "هوندا",
        },
        "name": "CG 125",
        "slug": "هوندا-cg-125",
        "production_start_year": 2010,
        "production_end_year": None,
        "engine_volume": 125,
        "description": (
            "مدل CG 125 مناسب انتخاب "
            "قطعات سازگار فروشگاه."
        ),
        "image": None,
        "is_active": True,
        "created_at": (
            "2026-09-02T11:00:00Z"
        ),
        "updated_at": (
            "2026-09-02T11:00:00Z"
        ),
    },
}


# =========================================================
# Motorcycle Model Create
# =========================================================


MotorcycleModelCreateSuccess = {
    "success": True,
    "message": (
        "موتورسیکلت با موفقیت "
        "ایجاد شد."
    ),
    "data": (
        MotorcycleModelDetailSuccess[
            "data"
        ]
    ),
}


# =========================================================
# Motorcycle Model Update
# =========================================================


MotorcycleModelUpdateSuccess = {
    "success": True,
    "message": (
        "موتورسیکلت با موفقیت "
        "بروزرسانی شد."
    ),
    "data": (
        MotorcycleModelDetailSuccess[
            "data"
        ]
    ),
}


# =========================================================
# Motorcycle Model Delete
# =========================================================


MotorcycleModelDeleteSuccess = {
    "success": True,
    "message": (
        "موتورسیکلت با موفقیت "
        "حذف شد."
    ),
    "data": None,
}


MotorcycleModelDeleteProtected = {
    "success": False,
    "message": (
        "این موتورسیکلت به "
        "اطلاعات دیگری وابسته است "
        "و قابل حذف نیست."
    ),
    "errors": None,
}


# =========================================================
# Validation Errors
# =========================================================


MotorcycleBrandDuplicateName = {
    "name": [
        "برندی با این نام "
        "قبلاً ثبت شده است."
    ],
}


MotorcycleModelDuplicateName = {
    "name": [
        (
            "این مدل برای برند "
            "انتخاب‌شده قبلاً "
            "ثبت شده است."
        )
    ],
}


MotorcycleModelInvalidYear = {
    "production_end_year": [
        (
            "سال پایان تولید نمی‌تواند "
            "قبل از سال شروع تولید باشد."
        )
    ],
}


MotorcycleInvalidImage = {
    "image": [
        (
            "فرمت تصویر مجاز نیست. "
            "فرمت‌های مجاز: "
            "JPEG, JPG, PNG, WEBP"
        )
    ],
}


# =========================================================
# Auth / Permission
# =========================================================


MotorcycleAuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    ),
}


MotorcyclePermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    ),
}


# =========================================================
# Not Found
# =========================================================


MotorcycleBrandNotFound = {
    "detail": (
        "No MotorcycleBrand matches "
        "the given query."
    ),
}


MotorcycleModelNotFound = {
    "detail": (
        "No MotorcycleModel matches "
        "the given query."
    ),
}