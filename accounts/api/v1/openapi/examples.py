SendOTPRequestExample = {
    "phone_number": "09196558273",
}

OTPVerifyRequestExample = {
    "phone_number": "09196558273",
    "otp_code": "123456",
}

CompleteProfileRequestExample = {
    "first_name": "امیر",
    "last_name": "مقدم",
}

LogoutRequestExample = {
    "refresh": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ),
}

TokenRefreshRequestExample = {
    "refresh": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ),
}
