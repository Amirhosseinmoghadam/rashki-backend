# =========================================================
# Send OTP
# =========================================================

SendOTPViewExample = {
    "phone_number": "09196558273",
}


# =========================================================
# Verify OTP
# =========================================================

OTPVerifyViewExample = {
    "phone_number": "09196558273",
    "otp_code": "123456",
}


# =========================================================
# Complete Profile
# =========================================================

CompleteProfileViewExample = {
    "first_name": "امیر",
    "last_name": "مقدم",
}


# =========================================================
# Logout
# =========================================================

UserLogoutAPIViewExample = {"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}



# =========================================================
# Address List
# =========================================================

AddressListAPIViewExample = {}


# =========================================================
# Address Create
# =========================================================

AddressCreateAPIViewExample = {
    "first_name": "امیر",
    "last_name": "مقدم",
    "mobile_number": "09196558273",
    "phone_number": "02112345678",
    "province": 1,
    "city": 1,
    "email": "amir@example.com",
    "postal_code": "1234567890",
    "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
    "is_default": True,
}


# =========================================================
# Address Detail
# =========================================================

AddressDetailAPIViewExample = {}


# =========================================================
# Address Update
# =========================================================

AddressUpdateAPIViewExample = {
    "first_name": "امیرحسین",
    "last_name": "مقدم",
    "mobile_number": "09196558273",
    "phone_number": "02112345678",
    "province": 1,
    "city": 1,
    "email": "amir@example.com",
    "postal_code": "1234567890",
    "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
    "is_default": True,
}


# =========================================================
# Address Partial Update
# =========================================================

AddressPartialUpdateAPIViewExample = {
    "postal_address": "تهران، خیابان ولیعصر، پلاک ۱۲۵",
}


# =========================================================
# Address Delete
# =========================================================

AddressDeleteAPIViewExample = {}


# =========================================================
# Set Default Address
# =========================================================

AddressSetDefaultAPIViewExample = {}