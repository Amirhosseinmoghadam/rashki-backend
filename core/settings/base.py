from datetime import timedelta
from pathlib import Path

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
    "carts",
    "categories",
    "contact",
    "discounts",
    "inventory",
    "motorcycles",
    "orders",
    "payments",
    "products",
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
            default=20,
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
# Swagger / OpenAPI
# =========================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Motorcycle Spare Parts API",
    "DESCRIPTION": (
        "API documentation for the motorcycle spare parts store."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}
