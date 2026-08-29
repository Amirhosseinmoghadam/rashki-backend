"""
OpenAPI Response definitions for Categories API.

This module contains response schemas used for API documentation.
"""

from categories.api.v1.openapi.schema import (
    CATEGORY_SCHEMA,
    CATEGORY_DETAIL_SCHEMA,
    CATEGORY_TREE_NODE_SCHEMA,
)

# Success response for list operation
CATEGORY_LIST_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "data": {
            "type": "array",
            "items": CATEGORY_SCHEMA,
        },
        "count": {"type": "integer", "example": 10},
    },
}

# Success response for retrieve operation
CATEGORY_RETRIEVE_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "data": CATEGORY_DETAIL_SCHEMA,
    },
}

# Success response for create operation
CATEGORY_CREATE_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "message": {"type": "string", "example": "Category created successfully."},
        "data": CATEGORY_DETAIL_SCHEMA,
    },
}

# Success response for update operation
CATEGORY_UPDATE_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "message": {"type": "string", "example": "Category updated successfully."},
        "data": CATEGORY_DETAIL_SCHEMA,
    },
}

# Success response for delete operation
CATEGORY_DELETE_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "message": {
            "type": "string",
            "example": "Category 'Electronics' deleted successfully.",
        },
    },
}

# Success response for tree operation
CATEGORY_TREE_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": True},
        "data": {
            "type": "array",
            "items": CATEGORY_TREE_NODE_SCHEMA,
        },
    },
}

# Error response for validation errors
VALIDATION_ERROR_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": False},
        "errors": {
            "type": "object",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
            "example": {
                "name": ["This field is required."],
                "slug": ["A category with this slug already exists."],
            },
        },
    },
}

# Error response for not found
NOT_FOUND_ERROR_RESPONSE = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": False},
        "error": {"type": "string", "example": "Category not found."},
    },
}

# Error response for authentication/permission errors
AUTH_ERROR_RESPONSE = {
    "type": "object",
    "properties": {
        "detail": {
            "type": "string",
            "example": "Authentication credentials were not provided.",
        },
    },
}
