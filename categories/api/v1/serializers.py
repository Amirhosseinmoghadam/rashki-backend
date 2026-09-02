from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

from categories.models import Category
from drf_spectacular.helpers import lazy_serializer

# =========================================================
# Category Child
# =========================================================


class CategoryChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "slug",
        ]


# =========================================================
# Category List
# =========================================================


class CategorySerializer(serializers.ModelSerializer):

    parent = serializers.IntegerField(
        source="parent_id",
        read_only=True,
    )

    children = serializers.SerializerMethodField()

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
            "slug",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(
        serializers.ListField(
            child=serializers.IntegerField()
        )
    )
    def get_children(self, obj):

        children = getattr(
            obj,
            "active_children",
            None,
        )

        if children is None:
            children = obj.children.filter(
                is_active=True
            )

        return [
            child.id
            for child in children
        ]


# =========================================================
# Category Detail
# =========================================================


class CategoryDetailSerializer(serializers.ModelSerializer):

    parent = serializers.SerializerMethodField()

    children = serializers.SerializerMethodField()

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

        read_only_fields = fields

    @extend_schema_field(
        CategoryChildSerializer(
            allow_null=True
        )
    )
    def get_parent(self, obj):

        if (
            obj.parent
            and obj.parent.is_active
        ):
            return CategoryChildSerializer(
                obj.parent
            ).data

        return None

    @extend_schema_field(
        CategoryChildSerializer(
            many=True
        )
    )
    def get_children(self, obj):

        children = getattr(
            obj,
            "active_children",
            None,
        )

        if children is None:
            children = obj.children.filter(
                is_active=True
            )

        return CategoryChildSerializer(
            children,
            many=True,
        ).data


# =========================================================
# Category Create / Update
# =========================================================


class CategoryCreateUpdateSerializer(
    serializers.ModelSerializer
):

    slug = serializers.CharField(
        read_only=True,
    )

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(
            is_active=True
        ),
        required=False,
        allow_null=True,
    )

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

        read_only_fields = [
            "slug",
        ]

    # =====================================================
    # Name
    # =====================================================

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "نام دسته‌بندی الزامی است."
            )

        return value

    # =====================================================
    # Parent
    # =====================================================

    def validate_parent(self, value):
        """
        Prevent circular hierarchy.

        Examples rejected:

            A -> A

            A -> B -> C -> A
        """

        if value is None:
            return value

        instance = self.instance

        if instance is None:
            return value

        # Direct self-reference
        if value.pk == instance.pk:
            raise serializers.ValidationError(
                "یک دسته‌بندی نمی‌تواند "
                "والد خودش باشد."
            )

        # Check ancestors
        parent = value

        visited = set()

        while parent is not None:

            if parent.pk in visited:
                raise serializers.ValidationError(
                    "ساختار دسته‌بندی دارای حلقه است."
                )

            visited.add(parent.pk)

            if parent.pk == instance.pk:
                raise serializers.ValidationError(
                    "انتخاب این دسته والد "
                    "باعث ایجاد حلقه می‌شود."
                )

            parent = parent.parent

        return value

# =========================================================
# Category Tree Serializer
# =========================================================


class CategoryTreeSerializer(serializers.Serializer):
    """
    Recursive serializer for category tree.

    Used for:

        GET /categories/tree/
    """

    id = serializers.IntegerField(
        read_only=True,
    )

    name = serializers.CharField(
        read_only=True,
    )

    slug = serializers.CharField(
        read_only=True,
    )

    image = serializers.URLField(
        allow_null=True,
        read_only=True,
    )

    children = serializers.SerializerMethodField()

    @extend_schema_field(
        lazy_serializer(
            "categories.api.v1.serializers.CategoryTreeSerializer"
        )(
            many=True
        )
    )
    def get_children(self, obj):
        """
        Recursively serialize child categories.
        """

        if isinstance(obj, dict):
            children = obj.get(
                "children",
                [],
            )

        else:
            children = getattr(
                obj,
                "children",
                [],
            )

        return CategoryTreeSerializer(
            children,
            many=True,
            context=self.context,
        ).data