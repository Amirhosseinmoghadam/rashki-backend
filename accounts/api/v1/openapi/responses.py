# =========================================================
# Send OTP
# =========================================================

SendOTPViewOTPSentSuccessfully = {
    "message": "کد تایید با موفقیت ارسال شد.",
    "expires_in": 120,
}


SendOTPViewRateLimitExceeded = {
    "detail": "تعداد درخواست‌ها بیش از حد مجاز است.",
    "retry_after": 45,
}


# =========================================================
# OTP Verify
# =========================================================

OTPVerifyViewSuccess = {
    "message": "احراز هویت با موفقیت انجام شد.",
    "is_new_user": False,
    "is_profile_completed": True,
    "next": "home",
    "user": {
        "id": 1,
        "phone_number": "09196558273",
        "first_name": "امیر",
        "last_name": "مقدم",
        "is_phone_verified": True,
    },
    "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    },
}


OTPVerifyViewSuccessNewUser = {
    "message": "احراز هویت با موفقیت انجام شد.",
    "is_new_user": True,
    "is_profile_completed": False,
    "next": "complete_profile",
    "user": {
        "id": 2,
        "phone_number": "09196558273",
        "first_name": "",
        "last_name": "",
        "is_phone_verified": True,
    },
    "tokens": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    },
}


OTPVerifyViewInvalidOTP = {
    "detail": "کد تایید معتبر نیست.",
}


OTPVerifyViewExpiredOTP = {
    "detail": "کد تایید منقضی شده است.",
}


OTPVerifyViewMaxAttemptsExceeded = {
    "detail": "تعداد تلاش‌های مجاز به پایان رسیده است.",
}


OTPVerifyViewInvalidCode = {
    "detail": "کد تایید اشتباه است.",
    "remaining_attempts": 2,
}


OTPVerifyViewRateLimitExceeded = {
    "detail": "تعداد تلاش‌های تایید بیش از حد مجاز است.",
    "retry_after": 60,
}


# =========================================================
# Complete Profile
# =========================================================

CompleteProfileViewSuccess = {
    "message": "اطلاعات کاربر با موفقیت تکمیل شد.",
    "is_profile_completed": True,
    "next": "home",
    "user": {
        "id": 1,
        "phone_number": "09196558273",
        "first_name": "امیر",
        "last_name": "مقدم",
        "is_phone_verified": True,
    },
}


# =========================================================
# Logout
# =========================================================

UserLogoutAPIViewSuccess = {
    "message": "Logout successful.",
}


UserLogoutAPIViewMissingRefreshToken = {
    "detail": "Refresh token is required.",
}


UserLogoutAPIViewInvalidRefreshToken = {
    "detail": "Refresh token is invalid or already blacklisted.",
}
