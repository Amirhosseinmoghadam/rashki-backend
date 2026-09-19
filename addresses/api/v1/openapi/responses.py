ProvinceListSuccess = {
    "success": True,
    "message": (
        "لیست استان‌ها با موفقیت دریافت شد."
    ),
    "data": [
        {"id": 1, "name": "تهران"},
        {"id": 2, "name": "سیستان و بلوچستان"},
    ],
}

CityListSuccess = {
    "success": True,
    "message": (
        "لیست شهرها با موفقیت دریافت شد."
    ),
    "data": [
        {"id": 1, "name": "تهران"},
        {"id": 2, "name": "ری"},
    ],
}

_address = {
    "id": 1,
    "first_name": "امیر",
    "last_name": "مقدم",
    "mobile_number": "09196558273",
    "phone_number": "02112345678",
    "province": 1,
    "province_name": "تهران",
    "city": 1,
    "city_name": "تهران",
    "postal_code": "1234567890",
    "postal_address": (
        "تهران، خیابان ولیعصر، پلاک ۱۲۳"
    ),
    "is_default": True,
    "created_at": "2026-09-12T12:00:00Z",
    "updated_at": "2026-09-12T12:00:00Z",
}

AddressListSuccess = {
    "success": True,
    "message": (
        "لیست آدرس‌ها با موفقیت دریافت شد."
    ),
    "data": [_address],
}

AddressCreateSuccess = {
    "success": True,
    "message": "آدرس با موفقیت ایجاد شد.",
    "data": _address,
}

AddressDetailSuccess = {
    "success": True,
    "message": "آدرس با موفقیت دریافت شد.",
    "data": _address,
}

AddressUpdateSuccess = {
    "success": True,
    "message": "آدرس با موفقیت بروزرسانی شد.",
    "data": {
        **_address,
        "first_name": "امیرحسین",
    },
}

AddressDeleteSuccess = {
    "success": True,
    "message": "آدرس با موفقیت حذف شد.",
    "data": None,
}

AddressSetDefaultSuccess = {
    "success": True,
    "message": (
        "آدرس پیش‌فرض با موفقیت تغییر کرد."
    ),
    "data": _address,
}

AddressNotFound = {
    "success": False,
    "message": "آدرس موردنظر پیدا نشد.",
    "errors": None,
}

AddressCityProvinceMismatch = {
    "city": [
        (
            "شهر انتخاب‌شده متعلق به "
            "استان انتخاب‌شده نیست."
        )
    ]
}

AddressCannotUnsetDefault = {
    "is_default": [
        (
            "نمی‌توانید آدرس پیش‌فرض را "
            "بدون انتخاب آدرس جدید حذف کنید."
        )
    ]
}

AddressAuthenticationRequired = {
    "detail": (
        "Authentication credentials were not provided."
    )
}
