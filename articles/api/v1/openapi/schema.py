"""
OpenAPI Schema definitions for Articles API
"""
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers


# Article Category Schemas
class ArticleCategoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=150)
    slug = serializers.SlugField(max_length=180, read_only=True)
    description = serializers.CharField(required=False)
    is_active = serializers.BooleanField(default=True)


class ArticleCategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False)
    is_active = serializers.BooleanField(default=True, required=False)


class ArticleListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=280, read_only=True)
    excerpt = serializers.CharField()
    cover_image = serializers.URLField(required=False)
    category = serializers.IntegerField()
    category_name = serializers.CharField(read_only=True)
    author = serializers.IntegerField()
    author_name = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(choices=[("draft", "draft"), ("published", "published"), ("archived", "archived")], default="draft")
    is_featured = serializers.BooleanField(default=False)
    reading_time = serializers.IntegerField(default=1)
    view_count = serializers.IntegerField(read_only=True, default=0)
    published_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(read_only=True)


class ArticleDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=280, read_only=True)
    excerpt = serializers.CharField()
    content = serializers.CharField()
    cover_image = serializers.URLField(required=False)
    category = serializers.IntegerField()
    category_name = serializers.CharField(read_only=True)
    author = serializers.IntegerField()
    author_name = serializers.CharField(read_only=True)
    products = serializers.ListField(child=serializers.IntegerField(), required=False)
    motorcycles = serializers.ListField(child=serializers.IntegerField(), required=False)
    status = serializers.ChoiceField(choices=[("draft", "draft"), ("published", "published"), ("archived", "archived")], default="draft")
    is_featured = serializers.BooleanField(default=False)
    reading_time = serializers.IntegerField(default=1)
    view_count = serializers.IntegerField(read_only=True, default=0)
    seo_title = serializers.CharField(max_length=255, required=False)
    meta_description = serializers.CharField(max_length=320, required=False)
    published_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ArticleCreateUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=280, required=False)
    excerpt = serializers.CharField(required=False)
    content = serializers.CharField()
    cover_image = serializers.ImageField(required=False)
    category = serializers.IntegerField()
    author = serializers.IntegerField(required=False)
    products = serializers.ListField(child=serializers.IntegerField(), required=False)
    motorcycles = serializers.ListField(child=serializers.IntegerField(), required=False)
    status = serializers.ChoiceField(choices=[("draft", "draft"), ("published", "published"), ("archived", "archived")], default="draft")
    is_featured = serializers.BooleanField(default=False, required=False)
    reading_time = serializers.IntegerField(default=1, required=False)
    seo_title = serializers.CharField(max_length=255, required=False)
    meta_description = serializers.CharField(max_length=320, required=False)
    published_at = serializers.DateTimeField(required=False)