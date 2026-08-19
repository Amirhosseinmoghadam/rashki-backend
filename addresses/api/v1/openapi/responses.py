# =========================================================
# Address List
# =========================================================

AddressListAPIViewSuccess = {
    "message": "لیست آدرس‌ها با موفقیت دریافت شد.",
    "addresses": [
        {
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
            "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
            "is_default": True,
            "created_at": "2026-08-18T18:30:00Z",
            "updated_at": "2026-08-18T18:30:00Z",
        },
        {
            "id": 2,
            "first_name": "امیر",
            "last_name": "مقدم",
            "mobile_number": "09196558273",
            "phone_number": "02187654321",
            "province": 1,
            "province_name": "تهران",
            "city": 2,
            "city_name": "ری",
            "postal_code": "1234567891",
            "postal_address": "ری، خیابان اصلی، پلاک ۴۵",
            "is_default": False,
            "created_at": "2026-08-17T15:20:00Z",
            "updated_at": "2026-08-17T15:20:00Z",
        },
    ],
}


# =========================================================
# Address Create
# =========================================================

AddressCreateAPIViewSuccess = {
    "message": "آدرس با موفقیت ایجاد شد.",
    "address": {
        "id": 3,
        "first_name": "امیر",
        "last_name": "مقدم",
        "mobile_number": "09196558273",
        "phone_number": "02112345678",
        "province": 1,
        "province_name": "تهران",
        "city": 1,
        "city_name": "تهران",
        "postal_code": "1234567890",
        "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
        "is_default": True,
        "created_at": "2026-08-18T18:30:00Z",
        "updated_at": "2026-08-18T18:30:00Z",
    },
}


# =========================================================
# Address Detail
# =========================================================

AddressDetailAPIViewSuccess = {
    "message": "آدرس با موفقیت دریافت شد.",
    "address": {
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
        "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
        "is_default": True,
        "created_at": "2026-08-18T18:30:00Z",
        "updated_at": "2026-08-18T18:30:00Z",
    },
}


# =========================================================
# Address Update
# =========================================================

AddressUpdateAPIViewSuccess = {
    "message": "آدرس با موفقیت بروزرسانی شد.",
    "address": {
        "id": 1,
        "first_name": "امیرحسین",
        "last_name": "مقدم",
        "mobile_number": "09196558273",
        "phone_number": "02112345678",
        "province": 1,
        "province_name": "تهران",
        "city": 1,
        "city_name": "تهران",
        "postal_code": "1234567890",
        "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۵",
        "is_default": True,
        "created_at": "2026-08-18T18:30:00Z",
        "updated_at": "2026-08-18T19:10:00Z",
    },
}


# =========================================================
# Address Delete
# =========================================================

AddressDeleteAPIViewSuccess = {
    "message": "آدرس با موفقیت حذف شد.",
}


# =========================================================
# Set Default Address
# =========================================================

AddressSetDefaultAPIViewSuccess = {
    "message": "آدرس پیش‌فرض با موفقیت تغییر کرد.",
    "address": {
        "id": 2,
        "first_name": "امیر",
        "last_name": "مقدم",
        "mobile_number": "09196558273",
        "phone_number": "02187654321",
        "province": 1,
        "province_name": "تهران",
        "city": 2,
        "city_name": "ری",
        "postal_code": "1234567891",
        "postal_address": "ری، خیابان اصلی، پلاک ۴۵",
        "is_default": True,
        "created_at": "2026-08-17T15:20:00Z",
        "updated_at": "2026-08-18T19:20:00Z",
    },
}


# =========================================================
# Common Errors
# =========================================================

AddressNotFound = {
    "detail": "آدرس موردنظر پیدا نشد.",
}


AddressValidationError = {
    "postal_code": [
        "کد پستی باید 10 رقم باشد."
    ],
}


AddressInvalidMobileNumber = {
    "mobile_number": [
        "شماره موبایل نامعتبر است."
    ],
}


AddressInvalidPhoneNumber = {
    "phone_number": [
        "شماره تلفن باید 11 رقم باشد."
    ],
}


AddressCityProvinceMismatch = {
    "city": [
        "شهر انتخاب‌شده متعلق به استان انتخاب‌شده نیست."
    ],
}


AddressCannotUnsetDefault = {
    "is_default": [
        "نمی‌توانید آدرس پیش‌فرض را بدون انتخاب آدرس جدید حذف کنید."
    ],
}


AddressAuthenticationRequired = {
    "detail": "Authentication credentials were not provided."
}