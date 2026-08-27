"""
OpenAPI Response definitions for Articles API
"""

from rest_framework import status
from articles.api.v1.openapi.schema import (
    ArticleCategoryListSerializer,
    ArticleCategoryCreateSerializer,
    ArticleListSerializer as ArticleListSchema,
    ArticleDetailSerializer as ArticleDetailSchema,
    ArticleCreateUpdateSerializer,
)

# Common responses
common_error_response = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"},
    },
    "example": {"detail": "Not found."},
}

validation_error_response = {
    "type": "object",
    "additionalProperties": {"type": "array", "items": {"type": "string"}},
    "example": {"title": ["This field is required."]},
}


# Article Category Responses
article_category_list_response = ArticleCategoryListSerializer(many=True)

article_category_detail_response = ArticleCategoryListSerializer()

article_category_create_response = ArticleCategoryCreateSerializer()


# Article Responses
article_list_response = ArticleListSchema(many=True)

article_detail_response = ArticleDetailSchema()

article_create_response = ArticleCreateUpdateSerializer()
