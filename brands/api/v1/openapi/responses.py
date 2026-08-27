"""
OpenAPI Response definitions for Brands API
"""

from drf_yasg import openapi
from .schema import brand_list_schema, brand_detail_schema, brand_create_schema

# Common responses
common_error_response = openapi.Response(
    description="Error response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "detail": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    examples={"application/json": {"detail": "Not found."}},
)

validation_error_response = openapi.Response(
    description="Validation error response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "field_name": openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)
            ),
        },
    ),
    examples={"application/json": {"name": ["This field is required."]}},
)


# Brand Responses
brand_list_response = openapi.Response(
    description="List of brands",
    schema=openapi.Schema(type=openapi.TYPE_ARRAY, items=brand_list_schema),
    examples={
        "application/json": [
            {
                "id": 1,
                "name": "هوندا",
                "slug": "honda",
                "logo": "https://example.com/media/brands/honda-logo.png",
                "description": "شرکت هوندا - تولیدکننده موتورسیکلت و خودرو",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "یاماها",
                "slug": "yamaha",
                "logo": "https://example.com/media/brands/yamaha-logo.png",
                "description": "شرکت یاماها - تولیدکننده موتورسیکلت",
                "is_active": True,
            },
        ]
    },
)

brand_detail_response = openapi.Response(
    description="Brand detail",
    schema=brand_detail_schema,
    examples={
        "application/json": {
            "id": 1,
            "name": "هوندا",
            "slug": "honda",
            "logo": "https://example.com/media/brands/honda-logo.png",
            "description": "شرکت هوندا - تولیدکننده موتورسیکلت و خودرو",
            "website": "https://www.honda.com",
            "is_active": True,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-15T14:00:00Z",
        }
    },
)

brand_create_response = openapi.Response(
    description="Brand created successfully",
    schema=brand_create_schema,
    examples={
        "application/json": {
            "name": "کاوازاکی",
            "slug": "kawasaki",
            "description": "شرکت کاوازاکی - تولیدکننده موتورسیکلت‌های اسپرت",
            "website": "https://www.kawasaki.com",
            "is_active": True,
        }
    },
)
