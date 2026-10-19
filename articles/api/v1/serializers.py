from rest_framework import serializers
from articles.models import ArticleCategory, Article



from django.utils.text import slugify
from rest_framework import serializers
from articles.models import ArticleCategory, Article


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
        ]
        read_only_fields = ["id", "slug"]

    def validate_name(self, value):
        return value.strip()

    def create(self, validated_data):
        name = validated_data["name"]

        base_slug = slugify(name, allow_unicode=True)

        if not base_slug:
            raise serializers.ValidationError({
                "name": "Cannot generate a valid slug."
            })

        slug = base_slug
        counter = 2

        while ArticleCategory.objects.filter(
            slug=slug
        ).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[:180 - len(suffix)]}{suffix}"
            counter += 1

        validated_data["slug"] = slug

        return super().create(validated_data)



class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for Article list view"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "cover_image",
            "category",
            "category_name",
            "author",
            "author_name",
            "status",
            "is_featured",
            "reading_time",
            "view_count",
            "published_at",
            "created_at",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Article detail view"""

    category_name = serializers.CharField(source="category.name", read_only=True)
    author_name = serializers.CharField(source="author.username", read_only=True)
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    motorcycles = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "cover_image",
            "category",
            "category_name",
            "author",
            "author_name",
            "products",
            "motorcycles",
            "status",
            "is_featured",
            "reading_time",
            "view_count",
            "seo_title",
            "meta_description",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "view_count", "created_at", "updated_at"]


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Article create and update operations"""

    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "excerpt",
            "content",
            "cover_image",
            "category",
            "author",
            "products",
            "motorcycles",
            "status",
            "is_featured",
            "reading_time",
            "seo_title",
            "meta_description",
            "published_at",
        ]
        read_only_fields = ["slug", "view_count", "created_at", "updated_at"]

    def validate_status(self, value):
        """Validate status field"""
        valid_statuses = [choice[0] for choice in Article.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {valid_statuses}"
            )
        return value
