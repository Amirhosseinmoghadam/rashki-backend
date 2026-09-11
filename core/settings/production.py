from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403, F401


# =========================================================
# Production
# =========================================================

DEBUG = False

ALLOWED_HOSTS = env.list(  # noqa: F405
    "ALLOWED_HOSTS",
    default=[],
)

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be configured in production."
    )


# =========================================================
# Database
# =========================================================

DATABASE_URL = env(  # noqa: F405
    "DATABASE_URL",
    default="",
)

if not DATABASE_URL:
    raise ImproperlyConfigured(
        "DATABASE_URL must be configured in production."
    )

DATABASES = {
    "default": env.db(  # noqa: F405
        "DATABASE_URL"
    )
}

DATABASES["default"]["CONN_MAX_AGE"] = env.int(  # noqa: F405
    "DB_CONN_MAX_AGE",
    default=60,
)

DATABASES["default"]["CONN_HEALTH_CHECKS"] = True


# =========================================================
# Redis
# =========================================================

REDIS_URL = env(  # noqa: F405
    "REDIS_URL",
    default="",
)

if not REDIS_URL:
    raise ImproperlyConfigured(
        "REDIS_URL must be configured in production."
    )

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": (
                "django_redis.client.DefaultClient"
            ),
        },
        "KEY_PREFIX": "motorcycle_store_prod",
        "TIMEOUT": 300,
    },
}


# =========================================================
# CORS / CSRF
# =========================================================

CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=[],
)

CSRF_TRUSTED_ORIGINS = env.list(  # noqa: F405
    "CSRF_TRUSTED_ORIGINS",
    default=[],
)


# =========================================================
# HTTPS / Cookies
# =========================================================

SECURE_SSL_REDIRECT = env.bool(  # noqa: F405
    "SECURE_SSL_REDIRECT",
    default=True,
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Enable only when a trusted reverse proxy sets and sanitizes
# X-Forwarded-Proto correctly (for example, a properly configured Nginx).
if env.bool(  # noqa: F405
    "TRUST_X_FORWARDED_PROTO",
    default=False,
):
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


# =========================================================
# HSTS / Security Headers
# =========================================================

SECURE_HSTS_SECONDS = env.int(  # noqa: F405
    "SECURE_HSTS_SECONDS",
    default=3600,
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(  # noqa: F405
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)

SECURE_HSTS_PRELOAD = env.bool(  # noqa: F405
    "SECURE_HSTS_PRELOAD",
    default=False,
)

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"


# =========================================================
# SMS - Required in Production
# =========================================================

MELIPAYAMAK = {
    "API_TOKEN": env("MELIPAYAMAK_API_TOKEN"),  # noqa: F405
    "DEFAULT_FROM": env("MELIPAYAMAK_DEFAULT_FROM"),  # noqa: F405
}


ZARINPAL_SANDBOX = False