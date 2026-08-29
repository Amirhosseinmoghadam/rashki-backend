from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.models import Category
from categories.api.v1.serializers import (
    CategorySerializer,
    CategoryDetailSerializer,
    CategoryCreateUpdateSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.

    Endpoints:

    GET     /categories/           -> List categories
    POST    /categories/           -> Create category (Admin)
    GET     /categories/{id}/      -> Retrieve category
    PUT     /categories/{id}/      -> Update category (Admin)
    PATCH   /categories/{id}/      -> Partial update (Admin)
    DELETE  /categories/{id}/      -> Delete category (Admin)

    GET     /categories/tree/      -> Category tree
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Category.objects.all()

    def get_permissions(self):
        """
        Allow authenticated users to read categories.
        Only admins can create, update, or delete categories.
        """

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsAuthenticated(), IsAdminUser()]

        if self.action == "tree":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Return filtered categories.

        Query parameters:

        ?parent=1
        ?search=engine
        """

        queryset = Category.objects.filter(is_active=True)

        # Filter by parent category
        parent_id = self.request.query_params.get("parent")

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        # Search by name or description
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_serializer_class(self):
        """
        Select serializer based on action.
        """

        if self.action == "retrieve":
            return CategoryDetailSerializer

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return CategoryCreateUpdateSerializer

        return CategorySerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new category.
        """

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "success": True,
                "message": "Category created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single category.
        """

        instance = self.get_object()

        serializer = self.get_serializer(instance)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        """
        Fully update a category.
        """

        partial = kwargs.pop("partial", False)

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "success": True,
                "message": "Category updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a category.
        """

        instance = self.get_object()

        category_name = instance.name

        self.perform_destroy(instance)

        return Response(
            {
                "success": True,
                "message": (f"Category '{category_name}' " "deleted successfully."),
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="tree",
    )
    def tree(self, request):
        """
        Return categories as a hierarchical tree.
        """

        categories = (
            Category.objects.filter(is_active=True)
            .select_related("parent")
            .prefetch_related("children")
        )

        def build_tree(parent=None):
            tree = []

            for category in categories:

                if category.parent_id == (parent.id if parent else None):
                    node = {
                        "id": category.id,
                        "name": category.name,
                        "slug": category.slug,
                        "image": (category.image.url if category.image else None),
                    }

                    children = build_tree(category)

                    if children:
                        node["children"] = children

                    tree.append(node)

            return tree

        return Response(
            {
                "success": True,
                "data": build_tree(),
            },
            status=status.HTTP_200_OK,
        )
