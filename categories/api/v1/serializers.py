# from rest_framework import serializers
#
# from categories.models import Category
#
#
# class CategorySerializer(serializers.ModelSerializer):
#     """Serializer for Category model with nested parent/children support."""
#
#     parent = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.filter(is_active=True),
#         required=False,
#         allow_null=True,
#         help_text="Parent category ID",
#     )
#     children = serializers.SerializerMethodField(
#         help_text="List of child category IDs",
#     )
#
#     class Meta:
#         model = Category
#         fields = [
#             "id",
#             "name",
#             "slug",
#             "parent",
#             "children",
#             "image",
#             "description",
#             "is_active",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = [
#             "id",
#             "created_at",
#             "updated_at",
#         ]
#
#     def get_children(self, obj):
#         """Return list of active child category IDs."""
#         if hasattr(obj, "children"):
#             return obj.children.filter(is_active=True).values_list("id", flat=True)
#         return []
#
#
# class CategoryDetailSerializer(serializers.ModelSerializer):
#     """Detailed serializer for Category with full nested information."""
#
#     parent = serializers.SerializerMethodField(
#         help_text="Parent category details",
#     )
#     children = serializers.SerializerMethodField(
#         help_text="List of child category details",
#     )
#
#     class Meta:
#         model = Category
#         fields = [
#             "id",
#             "name",
#             "slug",
#             "parent",
#             "children",
#             "image",
#             "description",
#             "is_active",
#             "created_at",
#             "updated_at",
#         ]
#         read_only_fields = [
#             "id",
#             "created_at",
#             "updated_at",
#         ]
#
#     def get_parent(self, obj):
#         """Return parent category details if exists."""
#         if obj.parent and obj.parent.is_active:
#             return {
#                 "id": obj.parent.id,
#                 "name": obj.parent.name,
#                 "slug": obj.parent.slug,
#             }
#         return None
#
#     def get_children(self, obj):
#         """Return list of active child category details."""
#         children = obj.children.filter(is_active=True) if hasattr(obj, "children") else []
#         return [
#             {
#                 "id": child.id,
#                 "name": child.name,
#                 "slug": child.slug,
#             }
#             for child in children
#         ]
#
#
# class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for creating and updating categories."""
#
#     class Meta:
#         model = Category
#         fields = [
#             "name",
#             "slug",
#             "parent",
#             "image",
#             "description",
#             "is_active",
#         ]
#
#     def validate_slug(self, value):
#         """Ensure slug is unique."""
#         queryset = Category.objects.all()
#         if self.instance:
#             queryset = queryset.exclude(pk=self.instance.pk)
#         if queryset.filter(slug=value).exists():
#             raise serializers.ValidationError("A category with this slug already exists.")
#         return value
#
#     def validate_parent(self, value):
#         """Prevent circular references in parent-child relationship."""
#         if value and self.instance:
#             # Check if the parent is the instance itself
#             if value == self.instance:
#                 raise serializers.ValidationError(
#                     "A category cannot be its own parent."
#                 )
#         return value
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from categories.models import Category

# =========================================================
# Category Child Serializer
# =========================================================


class CategoryChildSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used for nested category information.
    """

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


# =========================================================
# Category Serializer
# =========================================================


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.

    Parent is represented by its ID.
    Children are represented by a list of child category IDs.
    """

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        help_text="Parent category ID",
    )

    children = serializers.SerializerMethodField(
        help_text="List of child category IDs",
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "children",
            "image",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.ListField(child=serializers.IntegerField()))
    def get_children(self, obj):
        """
        Return active child category IDs.
        """

        return list(obj.children.filter(is_active=True).values_list("id", flat=True))


# =========================================================
# Category Detail Serializer
# =========================================================


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Category.

    Parent contains basic category information.
    Children contain basic information for each child category.
    """

    parent = serializers.SerializerMethodField(
        help_text="Parent category details",
    )

    children = serializers.SerializerMethodField(
        help_text="List of child category details",
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "children",
            "image",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(
        {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                    },
                    "required": [
                        "id",
                        "name",
                        "slug",
                    ],
                },
                {"type": "null"},
            ]
        }
    )
    def get_parent(self, obj):
        """
        Return parent category details if active.
        """

        if obj.parent and obj.parent.is_active:
            return {
                "id": obj.parent.id,
                "name": obj.parent.name,
                "slug": obj.parent.slug,
            }

        return None

    @extend_schema_field(CategoryChildSerializer(many=True))
    def get_children(self, obj):
        """
        Return active child category details.
        """

        children = obj.children.filter(is_active=True)

        return CategoryChildSerializer(children, many=True).data


# =========================================================
# Category Create / Update Serializer
# =========================================================


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating categories.
    """

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "parent",
            "image",
            "description",
            "is_active",
        ]

    def validate_slug(self, value):
        """
        Ensure slug is unique.
        """

        queryset = Category.objects.all()

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.filter(slug=value).exists():
            raise serializers.ValidationError(
                "A category with this slug already exists."
            )

        return value

    def validate_parent(self, value):
        """
        Prevent circular references in parent-child relationship.
        """

        if value and self.instance:

            # Prevent category from being its own parent
            if value == self.instance:
                raise serializers.ValidationError(
                    "A category cannot be its own parent."
                )

        return value
