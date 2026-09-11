from django.db.models import Q
from django.db.models.deletion import (
    ProtectedError,
)

from rest_framework import (
    status,
    viewsets,
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
)
from rest_framework.response import Response

from brands.models import Brand

from .serializers import (
    BrandListSerializer,
    BrandDetailSerializer,
    BrandCreateUpdateSerializer,
)

from .openapi.schema import (
    brand_list_view_schema,
    brand_detail_view_schema,
    brand_create_view_schema,
    brand_update_view_schema,
    brand_partial_update_view_schema,
    brand_delete_view_schema,
)


# =========================================================
# Brand ViewSet
# =========================================================


class BrandViewSet(
    viewsets.ModelViewSet
):
    """
    Brand API.

    Public:
        GET /brands/
        GET /brands/{id}/

    Admin:
        POST   /brands/
        PUT    /brands/{id}/
        PATCH  /brands/{id}/
        DELETE /brands/{id}/
    """

    pagination_class = None

    # =====================================================
    # Permissions
    # =====================================================

    def get_permissions(self):
        """
        Brand browsing is public.

        Creating, updating and deleting brands
        requires an admin/staff user.
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
    # QuerySet
    # =====================================================

    def get_queryset(self):
        """
        Public:
            Only active brands.

        Admin write actions:
            Active and inactive brands.

        List filters:
            ?search=ngk
        """

        queryset = Brand.objects.all()

        # -------------------------------------------------
        # Visibility
        # -------------------------------------------------

        if self.action not in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:

            queryset = queryset.filter(
                is_active=True
            )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        if self.action == "list":

            search = (
                self.request
                .query_params
                .get("search")
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

        if self.action == "list":

            return BrandListSerializer

        if self.action == "retrieve":

            return BrandDetailSerializer

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:

            return (
                BrandCreateUpdateSerializer
            )

        return BrandDetailSerializer

    # =====================================================
    # LIST
    # =====================================================

    @brand_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        serializer = BrandListSerializer(
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
                    "لیست برندها با موفقیت "
                    "دریافت شد."
                ),
                "count": len(
                    serializer.data
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # RETRIEVE
    # =====================================================

    @brand_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        brand = self.get_object()

        serializer = BrandDetailSerializer(
            brand,
            context=(
                self.get_serializer_context()
            ),
        )

        return Response(
            {
                "success": True,
                "message": (
                    "برند با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # CREATE
    # =====================================================

    @brand_create_view_schema
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = (
            BrandCreateUpdateSerializer(
                data=request.data,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        brand = serializer.save()

        response_serializer = (
            BrandDetailSerializer(
                brand,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "برند با موفقیت ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # UPDATE - PUT
    # =====================================================

    @brand_update_view_schema
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        partial = kwargs.pop(
            "partial",
            False,
        )

        brand = self.get_object()

        serializer = (
            BrandCreateUpdateSerializer(
                brand,
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

        brand = serializer.save()

        response_serializer = (
            BrandDetailSerializer(
                brand,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "برند با موفقیت "
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

    @brand_partial_update_view_schema
    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):

        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # DELETE
    # =====================================================

    @brand_delete_view_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        brand = self.get_object()

        try:

            brand.delete()

        except ProtectedError:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این برند به اطلاعات "
                        "دیگری وابسته است و "
                        "قابل حذف نیست."
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
                    "برند با موفقیت حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )