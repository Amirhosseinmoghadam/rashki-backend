"""
OpenAPI Schema definitions for Brands API
"""
from drf_yasg import openapi


# Brand Schemas
brand_list_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, read_only=True),
        "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=150),
        "slug": openapi.Schema(type=openapi.TYPE_STRING, max_length=180, read_only=True),
        "logo": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
    }
)

brand_detail_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, read_only=True),
        "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=150),
        "slug": openapi.Schema(type=openapi.TYPE_STRING, max_length=180, read_only=True),
        "logo": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
        "website": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
        "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, read_only=True),
    }
)

brand_create_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name'],
    properties={
        "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=150),
        "slug": openapi.Schema(type=openapi.TYPE_STRING, max_length=180),
        "logo": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY),
        "description": openapi.Schema(type=openapi.TYPE_STRING),
        "website": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
    }
)