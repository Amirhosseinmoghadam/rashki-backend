"""
OpenAPI Schema definitions for Categories API.

This module contains schema components used for API documentation.
"""

CATEGORY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "readOnly": True},
        "name": {"type": "string", "maxLength": 150},
        "slug": {"type": "string", "maxLength": 180, "pattern": "^[-a-zA-Z0-9_]+$"},
        "parent": {
            "oneOf": [{"type": "integer"}, {"type": "null"}],
            "description": "Parent category ID",
        },
        "children": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "List of child category IDs",
        },
        "image": {
            "oneOf": [{"type": "string", "format": "uri"}, {"type": "null"}],
            "description": "Category image URL",
        },
        "description": {"type": "string"},
        "is_active": {"type": "boolean", "default": True},
        "created_at": {"type": "string", "format": "date-time", "readOnly": True},
        "updated_at": {"type": "string", "format": "date-time", "readOnly": True},
    },
    "required": ["name", "slug"],
}

CATEGORY_DETAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "readOnly": True},
        "name": {"type": "string", "maxLength": 150},
        "slug": {"type": "string", "maxLength": 180},
        "parent": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                    },
                },
                {"type": "null"},
            ],
            "description": "Parent category details",
        },
        "children": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "slug": {"type": "string"},
                },
            },
            "description": "List of child category details",
        },
        "image": {"oneOf": [{"type": "string", "format": "uri"}, {"type": "null"}]},
        "description": {"type": "string"},
        "is_active": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time", "readOnly": True},
        "updated_at": {"type": "string", "format": "date-time", "readOnly": True},
    },
}

CATEGORY_CREATE_UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "maxLength": 150},
        "slug": {"type": "string", "maxLength": 180, "pattern": "^[-a-zA-Z0-9_]+$"},
        "parent": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
        "image": {"oneOf": [{"type": "string", "format": "binary"}, {"type": "null"}]},
        "description": {"type": "string"},
        "is_active": {"type": "boolean", "default": True},
    },
    "required": ["name", "slug"],
}

CATEGORY_TREE_NODE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "slug": {"type": "string"},
        "image": {"oneOf": [{"type": "string", "format": "uri"}, {"type": "null"}]},
        "children": {
            "type": "array",
            "items": {"$ref": "#/components/schemas/CategoryTreeNode"},
        },
    },
    "required": ["id", "name", "slug"],
}
