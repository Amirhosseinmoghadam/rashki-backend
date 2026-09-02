from django.db.models import Prefetch, Q
from django.db.models.deletion import ProtectedError

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from categories.models import Category

from .serializers import (
    CategorySerializer,
    CategoryDetailSerializer,
    CategoryCreateUpdateSerializer,
    CategoryTreeSerializer,
)

from .openapi.schema import (
    category_list_view_schema,
    category_detail_view_schema,
    category_create_view_schema,
    category_update_view_schema,
    category_partial_update_view_schema,
    category_delete_view_schema,
    category_tree_view_schema,
)


# =========================================================
# Category ViewSet
# =========================================================


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category API.

    Public:
        GET /categories/
        GET /categories/{id}/
        GET /categories/tree/

    Admin:
        POST   /categories/
        PUT    /categories/{id}/
        PATCH  /categories/{id}/
        DELETE /categories/{id}/
    """

    pagination_class = None

    # =====================================================
    # Permissions
    # =====================================================

    def get_permissions(self):
        """
        Category browsing is public.

        Creating, updating and deleting categories
        requires an admin user.
        """

        if self.action in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:
            return [
                IsAdminUser(),
            ]

        return [
            AllowAny(),
        ]

    # =====================================================
    # Public Category Visibility
    # =====================================================

    @staticmethod
    def _get_public_category_ids():
        """
        Return IDs of categories that are publicly visible.

        A category is publicly visible only when:

            - The category itself is active.
            - All of its ancestors are active.

        Example:

            Parent (inactive)
                └── Child (active)

        Child must NOT be visible publicly.
        """

        categories = list(
            Category.objects.all().values(
                "id",
                "parent_id",
                "is_active",
            )
        )

        category_map = {
            category["id"]: category
            for category in categories
        }

        visible_ids = set()

        # -------------------------------------------------
        # Root Categories
        # -------------------------------------------------

        for category in categories:

            if (
                category["parent_id"] is None
                and category["is_active"]
            ):
                visible_ids.add(
                    category["id"]
                )

        # -------------------------------------------------
        # Descendants
        # -------------------------------------------------

        changed = True

        while changed:

            changed = False

            for category in categories:

                category_id = category["id"]

                if category_id in visible_ids:
                    continue

                if not category["is_active"]:
                    continue

                parent_id = category["parent_id"]

                if parent_id in visible_ids:

                    visible_ids.add(
                        category_id
                    )

                    changed = True

        return visible_ids

    # =====================================================
    # QuerySet
    # =====================================================

    def get_queryset(self):
        """
        Return categories according to the current action.

        Public actions:
            Only publicly visible categories.

        Admin write actions:
            Active and inactive categories.

        List filters:

            ?parent=1
            ?parent=root
            ?search=ترمز
        """

        # -------------------------------------------------
        # Active children Prefetch
        # -------------------------------------------------

        active_children_queryset = (
            Category.objects.filter(
                is_active=True
            )
            .only(
                "id",
                "name",
                "slug",
                "parent_id",
            )
            .order_by(
                "name",
            )
        )

        queryset = (
            Category.objects
            .select_related(
                "parent",
            )
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=(
                        active_children_queryset
                    ),
                    to_attr="active_children",
                )
            )
        )

        # -------------------------------------------------
        # Public / Admin Visibility
        # -------------------------------------------------

        if self.action not in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:

            visible_ids = (
                self._get_public_category_ids()
            )

            queryset = queryset.filter(
                id__in=visible_ids
            )

        # -------------------------------------------------
        # List Filters
        # -------------------------------------------------

        if self.action == "list":

            # ---------------------------------------------
            # Parent
            # ---------------------------------------------

            parent = (
                self.request.query_params.get(
                    "parent"
                )
            )

            if parent:

                parent = parent.strip()

                if parent == "root":

                    queryset = queryset.filter(
                        parent__isnull=True
                    )

                else:

                    try:
                        parent_id = int(
                            parent
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        return queryset.none()

                    queryset = queryset.filter(
                        parent_id=parent_id
                    )

            # ---------------------------------------------
            # Search
            # ---------------------------------------------

            search = (
                self.request.query_params.get(
                    "search"
                )
            )

            if search:

                search = search.strip()

                if search:

                    queryset = queryset.filter(
                        Q(
                            name__icontains=search
                        )
                        |
                        Q(
                            description__icontains=search
                        )
                    )

        return queryset.order_by(
            "name"
        )

    # =====================================================
    # Serializer
    # =====================================================

    def get_serializer_class(self):
        """
        Select serializer based on action.
        """

        if self.action == "retrieve":

            return (
                CategoryDetailSerializer
            )

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:

            return (
                CategoryCreateUpdateSerializer
            )

        return CategorySerializer

    # =====================================================
    # LIST
    # =====================================================

    @category_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Return public categories.

        Optional filters:

            ?parent=root
            ?parent=1
            ?search=ترمز
        """

        queryset = (
            self.filter_queryset(
                self.get_queryset()
            )
        )

        serializer = CategorySerializer(
            queryset,
            many=True,
            context=(
                self.get_serializer_context()
            ),
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست دسته‌بندی‌ها "
                    "با موفقیت دریافت شد."
                ),
                "count": len(
                    serializer.data
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # CREATE
    # =====================================================

    @category_create_view_schema
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Create category.

        Admin only.

        Slug is generated automatically
        by the Category model.
        """

        serializer = (
            CategoryCreateUpdateSerializer(
                data=request.data,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = serializer.save()

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        response_serializer = (
            CategoryDetailSerializer(
                category,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "دسته‌بندی با موفقیت "
                    "ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # RETRIEVE
    # =====================================================

    @category_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Return a single publicly visible category.
        """

        category = self.get_object()

        serializer = (
            CategoryDetailSerializer(
                category,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "دسته‌بندی با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # UPDATE - PUT
    # =====================================================

    @category_update_view_schema
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Fully update category.

        Admin only.

        Slug remains unchanged.
        """

        partial = kwargs.pop(
            "partial",
            False,
        )

        category = self.get_object()

        serializer = (
            CategoryCreateUpdateSerializer(
                category,
                data=request.data,
                partial=partial,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = serializer.save()

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        response_serializer = (
            CategoryDetailSerializer(
                category,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "دسته‌بندی با موفقیت "
                    "بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PARTIAL UPDATE - PATCH
    # =====================================================

    @category_partial_update_view_schema
    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Partially update category.

        Admin only.
        """

        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # DELETE
    # =====================================================

    @category_delete_view_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Delete category.

        Admin only.

        Protected relationships prevent deletion
        when another object depends on this category.
        """

        category = self.get_object()

        try:

            category.delete()

        except ProtectedError:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این دسته‌بندی به "
                        "اطلاعات دیگری وابسته است "
                        "و قابل حذف نیست."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        return Response(
            {
                "success": True,
                "message": (
                    "دسته‌بندی با موفقیت "
                    "حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # CATEGORY TREE
    # =========================================================

    @category_tree_view_schema
    @action(
        detail=False,
        methods=[
            "get",
        ],
        url_path="tree",
    )
    def tree(
            self,
            request,
    ):
        """
        Return public categories as a hierarchy.
        """

        visible_ids = (
            self._get_public_category_ids()
        )

        categories = list(
            Category.objects.filter(
                id__in=visible_ids
            )
            .only(
                "id",
                "name",
                "slug",
                "image",
                "parent_id",
            )
            .order_by(
                "name"
            )
        )

        # =====================================================
        # Build Nodes
        # =====================================================

        nodes = {}

        for category in categories:

            image_url = None

            if category.image:
                image_url = (
                    request.build_absolute_uri(
                        category.image.url
                    )
                )

            nodes[category.id] = {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "image": image_url,
                "children": [],
            }

        # =====================================================
        # Build Tree
        # =====================================================

        roots = []

        for category in categories:

            node = nodes[
                category.id
            ]

            parent_id = (
                category.parent_id
            )

            if parent_id is None:
                roots.append(
                    node
                )

                continue

            parent_node = nodes.get(
                parent_id
            )

            if parent_node is None:
                continue

            parent_node[
                "children"
            ].append(
                node
            )

        serializer = CategoryTreeSerializer(
            roots,
            many=True,
            context=self.get_serializer_context(),
        )

        return Response(
            {
                "success": True,
                "message": (
                    "ساختار دسته‌بندی‌ها "
                    "با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )