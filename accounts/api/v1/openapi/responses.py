SendOTPSuccess = {
    "success": True,
    "message": "کد تایید با موفقیت ارسال شد.",
    "data": {
        "expires_in": 120,
    },
}

OTPVerifyExistingUserSuccess = {
    "success": True,
    "message": "احراز هویت با موفقیت انجام شد.",
    "data": {
        "is_new_user": False,
        "is_profile_completed": True,
        "next": "home",
        "user": {
            "id": 1,
            "phone_number": "09196558273",
            "first_name": "امیر",
            "last_name": "مقدم",
            "is_phone_verified": True,
            "is_profile_completed": True,
        },
        "tokens": {
            "refresh": "refresh-token...",
            "access": "access-token...",
        },
    },
}

OTPVerifyNewUserSuccess = {
    "success": True,
    "message": "احراز هویت با موفقیت انجام شد.",
    "data": {
        "is_new_user": True,
        "is_profile_completed": False,
        "next": "complete_profile",
        "user": {
            "id": 2,
            "phone_number": "09196558273",
            "first_name": "",
            "last_name": "",
            "is_phone_verified": True,
            "is_profile_completed": False,
        },
        "tokens": {
            "refresh": "refresh-token...",
            "access": "access-token...",
        },
    },
}

ProfileSuccess = {
    "success": True,
    "message": "اطلاعات کاربر با موفقیت دریافت شد.",
    "data": {
        "id": 1,
        "phone_number": "09196558273",
        "first_name": "امیر",
        "last_name": "مقدم",
        "is_phone_verified": True,
        "is_profile_completed": True,
    },
}

LogoutSuccess = {
    "success": True,
    "message": "خروج از حساب با موفقیت انجام شد.",
    "data": None,
}

TokenRefreshSuccess = {
    "success": True,
    "message": "Access token با موفقیت بروزرسانی شد.",
    "data": {
        "access": "new-access-token...",
    },
}

ValidationError = {
    "success": False,
    "message": "اطلاعات ارسالی معتبر نیست.",
    "errors": {
        "phone_number": [
            "شماره تلفن همراه باید با 09 شروع شود و ۱۱ رقم باشد."
        ]
    },
}

RateLimitError = {
    "success": False,
    "message": "تعداد درخواست‌ها بیش از حد مجاز است.",
    "errors": {
        "retry_after": 60,
        "reason": "resend",
    },
}

InvalidOTPError = {
    "success": False,
    "message": "کد تایید اشتباه است.",
    "errors": {
        "code": "otp_code_mismatch",
        "remaining_attempts": 2,
    },
}

InactiveUserError = {
    "success": False,
    "message": "حساب کاربری غیرفعال است.",
    "errors": {
        "code": "inactive_user",
    },
}
