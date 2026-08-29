"""
OpenAPI Example definitions for Categories API.

This module contains example data used for API documentation.
"""

# Example category data
CATEGORY_EXAMPLE = {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "parent": None,
    "children": [2, 3],
    "image": "https://example.com/media/categories/electronics.jpg",
    "description": "Electronic devices and accessories",
    "is_active": True,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z",
}

CATEGORY_DETAIL_EXAMPLE = {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "parent": None,
    "children": [
        {"id": 2, "name": "Mobile Phones", "slug": "mobile-phones"},
        {"id": 3, "name": "Laptops", "slug": "laptops"},
    ],
    "image": "https://example.com/media/categories/electronics.jpg",
    "description": "Electronic devices and accessories",
    "is_active": True,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z",
}

CATEGORY_CREATE_EXAMPLE = {
    "name": "Mobile Phones",
    "slug": "mobile-phones",
    "parent": 1,
    "image": None,
    "description": "Smartphones and feature phones",
    "is_active": True,
}

CATEGORY_UPDATE_EXAMPLE = {
    "name": "Mobile Phones & Accessories",
    "slug": "mobile-phones",
    "parent": 1,
    "description": "Smartphones, feature phones, and accessories",
    "is_active": True,
}

CATEGORY_TREE_EXAMPLE = [
    {
        "id": 1,
        "name": "Electronics",
        "slug": "electronics",
        "image": "https://example.com/media/categories/electronics.jpg",
        "children": [
            {
                "id": 2,
                "name": "Mobile Phones",
                "slug": "mobile-phones",
                "image": None,
                "children": [],
            },
            {
                "id": 3,
                "name": "Laptops",
                "slug": "laptops",
                "image": None,
                "children": [
                    {
                        "id": 4,
                        "name": "Gaming Laptops",
                        "slug": "gaming-laptops",
                        "image": None,
                        "children": [],
                    }
                ],
            },
        ],
    },
    {
        "id": 5,
        "name": "Clothing",
        "slug": "clothing",
        "image": "https://example.com/media/categories/clothing.jpg",
        "children": [],
    },
]

# Error examples
VALIDATION_ERROR_EXAMPLE = {
    "success": False,
    "errors": {
        "name": ["This field is required."],
        "slug": ["A category with this slug already exists."],
    },
}

NOT_FOUND_ERROR_EXAMPLE = {
    "success": False,
    "error": "Category not found.",
}

AUTH_ERROR_EXAMPLE = {
    "detail": "Authentication credentials were not provided.",
}
