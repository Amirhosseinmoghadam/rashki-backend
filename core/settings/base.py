from datetime import timedelta
from pathlib import Path
import os
import environ


# =========================================================
# Paths / Environment
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# =========================================================
# Core Security
# =========================================================

SECRET_KEY = env("DJANGO_SECRET_KEY")
JWT_SIGNING_KEY = env("JWT_SIGNING_KEY")
AUTH_OTP_HMAC_KEY = env("AUTH_OTP_HMAC_KEY")

DEBUG = False

ALLOWED_HOSTS = []


# =========================================================
# Applications
# =========================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # External
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_extensions",

    # Internal
    "accounts",
    "addresses",
    "articles",
    "brands",
    "carts.apps.CartsConfig",
    "categories",
    "contact",
    "discounts",
    "shipping",
    #"inventory",
    "motorcycles",
    "orders",
    "payments.apps.PaymentsConfig",
    "products",
    "pricing",
    "wishlists",
]


# =========================================================
# Middleware
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URL / Templates / WSGI / ASGI
# =========================================================

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"


# =========================================================
# Database
# =========================================================
# Environment-specific. Defined in development.py / production.py.

DATABASES = {}


# =========================================================
# Cache / Redis
# =========================================================
# Environment-specific. Defined in development.py / production.py.

CACHES = {}


# =========================================================
# Password Validation
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =========================================================
# Internationalization
# =========================================================

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"

USE_I18N = True
USE_TZ = True


# =========================================================
# Static / Media
# =========================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# Image Upload
# =========================================================

MAX_IMAGE_UPLOAD_SIZE = env.int(
    "MAX_IMAGE_UPLOAD_SIZE",
    default=10 * 1024 * 1024,
)

MAX_IMAGE_PIXEL_COUNT = env.int(
    "MAX_IMAGE_PIXEL_COUNT",
    default=40_000_000,
)

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}


# =========================================================
# Custom User
# =========================================================

AUTH_USER_MODEL = "accounts.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# Django REST Framework
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
    "DEFAULT_THROTTLE_RATES": {
        "contact": env(
            "CONTACT_THROTTLE_RATE",
            default="5/hour",
        ),
    },
}


# =========================================================
# JWT
# =========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int(
            "JWT_ACCESS_MINUTES",
            default=180,
        )
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int(
            "JWT_REFRESH_DAYS",
            default=30,
        )
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": JWT_SIGNING_KEY,
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}

# =========================================================
# Order
# =========================================================
# کاربر بعد از ایجاد Order
# چند دقیقه فرصت دارد پرداخت را انجام دهد.
ORDER_PAYMENT_TIMEOUT_MINUTES = 20

# =========================================================
# CORS / CSRF
# =========================================================
# Allowed origins are environment-specific.

CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOW_CREDENTIALS = False

CORS_ALLOWED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = []


# =========================================================
# SMS
# =========================================================

MELIPAYAMAK = {
    "API_TOKEN": env(
        "MELIPAYAMAK_API_TOKEN",
        default="",
    ),
    "DEFAULT_FROM": env(
        "MELIPAYAMAK_DEFAULT_FROM",
        default="",
    ),
}
# =========================================================
# Tipax API
# =========================================================


TIPAX_BASE_URL = os.getenv(
    "TIPAX_BASE_URL",
    "https://omtestapi.tipax.ir",
).rstrip("/")


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------


# برای Production بهتر است Username/Password/API Key
# قرار داده شوند تا Backend بتواند Token جدید بگیرد.
TIPAX_USERNAME = os.getenv(
    "TIPAX_USERNAME",
    "",
)

TIPAX_PASSWORD = os.getenv(
    "TIPAX_PASSWORD",
    "",
)

TIPAX_API_KEY = os.getenv(
    "TIPAX_API_KEY",
    "",
)


# Token اولیه.
#
# فقط در ENV قرار بگیرد.
TIPAX_ACCESS_TOKEN = os.getenv(
    "TIPAX_ACCESS_TOKEN",
    "",
)

TIPAX_REFRESH_TOKEN = os.getenv(
    "TIPAX_REFRESH_TOKEN",
    "",
)


# ---------------------------------------------------------
# HTTP
# ---------------------------------------------------------


TIPAX_HTTP_TIMEOUT_SECONDS = int(
    os.getenv(
        "TIPAX_HTTP_TIMEOUT_SECONDS",
        "20",
    )
)


# ---------------------------------------------------------
# Money
# ---------------------------------------------------------
#
# مستندات عمومی‌ای که داریم واحد دقیق تمام Amountهای API
# را صریح مشخص نکرده‌اند.
#
# اگر API مبلغ را تومان می‌دهد:
#     1
#
# اگر API مبلغ را ریال می‌دهد:
#     10
#
# بنابراین عمداً قابل تنظیم است.
# ---------------------------------------------------------


TIPAX_AMOUNT_DIVISOR_TO_TOMAN = int(
    os.getenv(
        "TIPAX_AMOUNT_DIVISOR_TO_TOMAN",
        "1",
    )
)


# ---------------------------------------------------------
# API Paths
# ---------------------------------------------------------
TIPAX_BASE_URL = os.getenv(
    "TIPAX_BASE_URL",
    "https://omtestapi.tipax.ir",
).rstrip("/")

TIPAX_USERNAME = os.getenv(
    "TIPAX_USERNAME",
    "",
)

TIPAX_PASSWORD = os.getenv(
    "TIPAX_PASSWORD",
    "",
)

TIPAX_API_KEY = os.getenv(
    "TIPAX_API_KEY",
    "",
)

TIPAX_ACCESS_TOKEN = os.getenv(
    "TIPAX_ACCESS_TOKEN",
    "",
)

TIPAX_REFRESH_TOKEN = os.getenv(
    "TIPAX_REFRESH_TOKEN",
    "",
)

TIPAX_HTTP_TIMEOUT_SECONDS = int(
    os.getenv(
        "TIPAX_HTTP_TIMEOUT_SECONDS",
        "20",
    )
)

TIPAX_AMOUNT_DIVISOR_TO_TOMAN = int(
    os.getenv(
        "TIPAX_AMOUNT_DIVISOR_TO_TOMAN",
        "1",
    )
)


TIPAX_TOKEN_PATH = (
    "/api/OM/v3/Account/token"
)

TIPAX_REFRESH_TOKEN_PATH = (
    "/api/OM/v3/Account/RefreshToken"
)

TIPAX_PRICING_PATH = (
    "/api/OM/v3/Pricing"
)

TIPAX_ORDERS_PATH = (
    "/api/OM/v3/Orders"
)

TIPAX_PACK_CONTENT_RATES_PATH = (
    "/api/OM/v3/PackContentRates"
)

TIPAX_PACKING_PRICES_PATH = (
    "/api/OM/v3/PackingPrices"
)

TIPAX_PARCEL_TYPES_PATH = (
    "/api/OM/v3/ParcelType/Search"
)

TIPAX_PAYMENT_TYPES_PATH = (
    "/api/OM/v3/PaymentType/Search"
)

TIPAX_CITIES_PATH = (
    "/api/OM/v3/Cities"
)

TIPAX_BRIEF_TRACKING_PATH = (
    "/api/OM/v3/Tracking/"
    "BriefTracking/{tracking_code}"
)

TIPAX_TRACK_BY_ORDER_PATH = (
    "/api/OM/v3/Tracking/{order_id}"
)

TIPAX_CANCEL_ORDER_PATH = (
    "/api/OM/v3/Orders/"
    "CancelOrder/{order_id}"
)

TIPAX_SERVICES_BETWEEN_CITIES_PATH = (
    "/api/OM/v3/Pricing/"
    "GetServicesBetweenCities"
)
# =========================================================
# Authentication / OTP
# =========================================================

AUTH_PHONE_REGEX_PATTERN = r"^09\d{9}$"

AUTH_OTP_LENGTH = env.int(
    "AUTH_OTP_LENGTH",
    default=6,
)

AUTH_OTP_EXPIRE_SECONDS = env.int(
    "AUTH_OTP_EXPIRE_SECONDS",
    default=120,
)

AUTH_OTP_MAX_ATTEMPTS = env.int(
    "AUTH_OTP_MAX_ATTEMPTS",
    default=5,
)

# Send OTP
AUTH_OTP_RESEND_SECONDS = env.int(
    "AUTH_OTP_RESEND_SECONDS",
    default=60,
)

AUTH_OTP_MAX_SENDS_PER_HOUR = env.int(
    "AUTH_OTP_MAX_SENDS_PER_HOUR",
    default=5,
)

AUTH_OTP_MAX_SENDS_PER_IP_WINDOW = env.int(
    "AUTH_OTP_MAX_SENDS_PER_IP_WINDOW",
    default=30,
)

AUTH_OTP_IP_WINDOW_SECONDS = env.int(
    "AUTH_OTP_IP_WINDOW_SECONDS",
    default=10 * 60,
)

# Verify OTP
AUTH_OTP_MAX_VERIFY_PER_WINDOW = env.int(
    "AUTH_OTP_MAX_VERIFY_PER_WINDOW",
    default=20,
)

AUTH_OTP_VERIFY_WINDOW_SECONDS = env.int(
    "AUTH_OTP_VERIFY_WINDOW_SECONDS",
    default=10 * 60,
)

AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW = env.int(
    "AUTH_OTP_MAX_VERIFY_PER_IP_WINDOW",
    default=60,
)

AUTH_OTP_VERIFY_IP_WINDOW_SECONDS = env.int(
    "AUTH_OTP_VERIFY_IP_WINDOW_SECONDS",
    default=10 * 60,
)

# =========================================================
# Payments
# =========================================================


# Timeout درخواست‌های HTTP به Providerها.
PAYMENT_HTTP_TIMEOUT_SECONDS = int(
    os.getenv(
        "PAYMENT_HTTP_TIMEOUT_SECONDS",
        "15",
    )
)


# =========================================================
# Frontend Payment Result
# =========================================================


# بعد از Callback موفق، Backend مرورگر را
# به این صفحه Frontend هدایت می‌کند.
PAYMENT_SUCCESS_REDIRECT_URL = os.getenv(
    "PAYMENT_SUCCESS_REDIRECT_URL",
    "http://localhost:5173/payment/success",
)


# بعد از پرداخت ناموفق یا لغوشده.
PAYMENT_FAILED_REDIRECT_URL = os.getenv(
    "PAYMENT_FAILED_REDIRECT_URL",
    "http://localhost:5173/payment/failed",
)


# =========================================================
# ZarinPal
# =========================================================


ZARINPAL_MERCHANT_ID = os.getenv(
    "ZARINPAL_MERCHANT_ID",
    "",
)


# کل سیستم ما تومان است.
#
# IRT = Toman
# IRR = Rial
#
# اگر Merchant/API شما Rial خواست،
# فقط ENV را IRR می‌کنیم.
ZARINPAL_PROVIDER_CURRENCY = os.getenv(
    "ZARINPAL_PROVIDER_CURRENCY",
    "IRT",
).upper()


ZARINPAL_REQUEST_URL = os.getenv(
    "ZARINPAL_REQUEST_URL",
    (
        "https://api.zarinpal.com/"
        "pg/v4/payment/request.json"
    ),
)


ZARINPAL_VERIFY_URL = os.getenv(
    "ZARINPAL_VERIFY_URL",
    (
        "https://api.zarinpal.com/"
        "pg/v4/payment/verify.json"
    ),
)


ZARINPAL_GATEWAY_URL = os.getenv(
    "ZARINPAL_GATEWAY_URL",
    (
        "https://www.zarinpal.com/"
        "pg/StartPay/"
    ),
)


# =========================================================
# TCart
# =========================================================


TCART_API_TOKEN = os.getenv(
    "TCART_API_TOKEN",
    "",
)


TCART_WEBHOOK_SECRET = os.getenv(
    "TCART_WEBHOOK_SECRET",
    "",
)


# این موارد را بعد از دریافت مستندات دقیق TCart
# تنظیم می‌کنیم.
TCART_CREATE_INVOICE_URL = os.getenv(
    "TCART_CREATE_INVOICE_URL",
    "",
)

TCART_INVOICE_STATUS_URL = os.getenv(
    "TCART_INVOICE_STATUS_URL",
    "",
)
# =========================================================
# Swagger / OpenAPI
# =========================================================

SPECTACULAR_SETTINGS = {

    "TITLE": (
        "Motorcycle Spare Parts API"
    ),

    "DESCRIPTION": (
        "API documentation for the "
        "motorcycle spare parts store."
    ),

    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,

    "COMPONENT_SPLIT_REQUEST": True,

    # =====================================================
    # Enum Names
    # =====================================================
    #
    # خود TextChoices class را معرفی می‌کنیم.
    # drf-spectacular خودش .choices را استخراج می‌کند.
    #
    # این کار از:
    #
    #   Status96cEnum
    #   Provider67eEnum
    #
    # و نام‌های Hashدار جلوگیری می‌کند.
    # =====================================================

    "ENUM_NAME_OVERRIDES": {

    # =====================================================
    # Products
    # =====================================================

    "ProductStatusEnum": (
        "products.models.Product.Status"
    ),


    # =====================================================
    # Articles
    # =====================================================

    # Request:
    # draft -> پیش‌نویس
    # published -> منتشر شده
    # archived -> بایگانی
    "ArticleStatusEnum": (
        "articles.models.Article.Status"
    ),

    # Response:
    # draft -> draft
    # published -> published
    # archived -> archived
    #
    # drf-spectacular این Choice Set را به علت
    # متفاوت بودن Labelها جدا تشخیص می‌دهد.
    "ArticleStatusResponseEnum": [
        "draft",
        "published",
        "archived",
    ],


    # =====================================================
    # Orders
    # =====================================================

    "OrderStatusEnum": (
        "orders.models.Order.Status"
    ),

    "OrderPaymentStatusEnum": (
        "orders.models.Order.PaymentStatus"
    ),


    # =====================================================
    # Payments
    # =====================================================

    "PaymentAttemptStatusEnum": (
        "payments.models.PaymentAttempt.Status"
    ),

    "PaymentProviderEnum": (
        "payments.models.PaymentAttempt.Provider"
    ),

    "PaymentRefundStatusEnum": (
        "payments.models.PaymentRefund.Status"
    ),


    # =====================================================
    # Shipping
    # =====================================================

    "ShipmentStatusEnum": (
        "shipping.models.Shipment.Status"
    ),

    "ShippingProviderEnum": (
        "shipping.models.ShippingMethod.Provider"
    ),
},
}