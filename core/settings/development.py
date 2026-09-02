from .base import *  # noqa: F403, F401


# =========================================================
# Development
# =========================================================

DEBUG = True

ALLOWED_HOSTS = env.list(  # noqa: F405
    "ALLOWED_HOSTS",
    default=[
        "localhost",
        "127.0.0.1",
    ],
)


# =========================================================
# Database
# =========================================================
# PostgreSQL is recommended for this project because code paths using
# select_for_update() should be tested against a database that supports
# row-level locking.
#
# If DATABASE_URL is omitted, SQLite is used only as a convenient fallback.

DATABASES = {
    "default": env.db(  # noqa: F405
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # noqa: F405
    )
}


# =========================================================
# Redis
# =========================================================

REDIS_URL = env(  # noqa: F405
    "REDIS_URL",
    default="redis://127.0.0.1:6379/1",
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
        "KEY_PREFIX": "motorcycle_store_dev",
    },
}


# =========================================================
# CORS / CSRF
# =========================================================

CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)

CSRF_TRUSTED_ORIGINS = env.list(  # noqa: F405
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)


# =========================================================
# Development Security
# =========================================================

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
