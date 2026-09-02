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

from motorcycles.models import (
    MotorcycleBrand,
    MotorcycleModel,
)

from .serializers import (
    MotorcycleBrandListSerializer,
    MotorcycleBrandDetailSerializer,
    MotorcycleBrandCreateUpdateSerializer,
    MotorcycleModelListSerializer,
    MotorcycleModelDetailSerializer,
    MotorcycleModelCreateUpdateSerializer,
)

from .openapi.schema import (
    motorcycle_brand_list_view_schema,
    motorcycle_brand_detail_view_schema,
    motorcycle_brand_create_view_schema,
    motorcycle_brand_update_view_schema,
    motorcycle_brand_partial_update_view_schema,
    motorcycle_brand_delete_view_schema,
    motorcycle_model_list_view_schema,
    motorcycle_model_detail_view_schema,
    motorcycle_model_create_view_schema,
    motorcycle_model_update_view_schema,
    motorcycle_model_partial_update_view_schema,
    motorcycle_model_delete_view_schema,
)


# =========================================================
# Motorcycle Brand ViewSet
# =========================================================


class MotorcycleBrandViewSet(
    viewsets.ModelViewSet
):

    pagination_class = None

    # =====================================================
    # Permissions
    # =====================================================

    def get_permissions(self):

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

        queryset = (
            MotorcycleBrand.objects.all()
        )

        # Public visibility
        if self.action not in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:

            queryset = queryset.filter(
                is_active=True
            )

        # Search
        if self.action == "list":

            search = (
                self.request
                .query_params
                .get("search")
            )

            if search:

                search = search.strip()

                if search:

                    queryset = (
                        queryset.filter(
                            name__icontains=search
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
            return (
                MotorcycleBrandListSerializer
            )

        if self.action == "retrieve":
            return (
                MotorcycleBrandDetailSerializer
            )

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return (
                MotorcycleBrandCreateUpdateSerializer
            )

        return (
            MotorcycleBrandDetailSerializer
        )

    # =====================================================
    # LIST
    # =====================================================

    @motorcycle_brand_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        serializer = (
            MotorcycleBrandListSerializer(
                queryset,
                many=True,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست برندهای موتورسیکلت "
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
    # RETRIEVE
    # =====================================================

    @motorcycle_brand_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        brand = self.get_object()

        serializer = (
            MotorcycleBrandDetailSerializer(
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
                    "برند موتورسیکلت "
                    "با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # CREATE
    # =====================================================

    @motorcycle_brand_create_view_schema
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = (
            MotorcycleBrandCreateUpdateSerializer(
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
            MotorcycleBrandDetailSerializer(
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
                    "برند موتورسیکلت "
                    "با موفقیت ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # UPDATE
    # =====================================================

    @motorcycle_brand_update_view_schema
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
            MotorcycleBrandCreateUpdateSerializer(
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
            MotorcycleBrandDetailSerializer(
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
                    "برند موتورسیکلت "
                    "با موفقیت بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PARTIAL UPDATE
    # =====================================================

    @motorcycle_brand_partial_update_view_schema
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

    @motorcycle_brand_delete_view_schema
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
                        "این برند دارای مدل "
                        "یا اطلاعات وابسته است "
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
                    "برند موتورسیکلت "
                    "با موفقیت حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Motorcycle Model ViewSet
# =========================================================


class MotorcycleModelViewSet(
    viewsets.ModelViewSet
):

    pagination_class = None

    # =====================================================
    # Permissions
    # =====================================================

    def get_permissions(self):

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

        queryset = (
            MotorcycleModel.objects
            .select_related(
                "brand"
            )
        )

        # -------------------------------------------------
        # Public Visibility
        # -------------------------------------------------

        if self.action not in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:

            queryset = queryset.filter(
                is_active=True,
                brand__is_active=True,
            )

        # -------------------------------------------------
        # Filters
        # -------------------------------------------------

        if self.action == "list":

            # Brand filter
            brand = (
                self.request
                .query_params
                .get("brand")
            )

            if brand:

                try:

                    brand_id = int(
                        brand
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    return queryset.none()

                queryset = queryset.filter(
                    brand_id=brand_id
                )

            # Engine volume filter
            engine_volume = (
                self.request
                .query_params
                .get("engine_volume")
            )

            if engine_volume:

                try:

                    engine_volume = int(
                        engine_volume
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    return queryset.none()

                queryset = queryset.filter(
                    engine_volume=engine_volume
                )

            # Search
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
                            brand__name__icontains=search
                        )
                        |
                        Q(
                            description__icontains=search
                        )
                    )

        return queryset.order_by(
            "brand__name",
            "name",
        )

    # =====================================================
    # Serializer
    # =====================================================

    def get_serializer_class(self):

        if self.action == "list":
            return (
                MotorcycleModelListSerializer
            )

        if self.action == "retrieve":
            return (
                MotorcycleModelDetailSerializer
            )

        if self.action in {
            "create",
            "update",
            "partial_update",
        }:
            return (
                MotorcycleModelCreateUpdateSerializer
            )

        return (
            MotorcycleModelDetailSerializer
        )

    # =====================================================
    # LIST
    # =====================================================

    @motorcycle_model_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        serializer = (
            MotorcycleModelListSerializer(
                queryset,
                many=True,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست موتورسیکلت‌ها "
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
    # RETRIEVE
    # =====================================================

    @motorcycle_model_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        motorcycle = self.get_object()

        serializer = (
            MotorcycleModelDetailSerializer(
                motorcycle,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "موتورسیکلت با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # CREATE
    # =====================================================

    @motorcycle_model_create_view_schema
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = (
            MotorcycleModelCreateUpdateSerializer(
                data=request.data,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        motorcycle = serializer.save()

        response_serializer = (
            MotorcycleModelDetailSerializer(
                motorcycle,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "موتورسیکلت با موفقیت "
                    "ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # UPDATE
    # =====================================================

    @motorcycle_model_update_view_schema
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

        motorcycle = self.get_object()

        serializer = (
            MotorcycleModelCreateUpdateSerializer(
                motorcycle,
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

        motorcycle = serializer.save()

        response_serializer = (
            MotorcycleModelDetailSerializer(
                motorcycle,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "موتورسیکلت با موفقیت "
                    "بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PARTIAL UPDATE
    # =====================================================

    @motorcycle_model_partial_update_view_schema
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

    @motorcycle_model_delete_view_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        motorcycle = self.get_object()

        try:

            motorcycle.delete()

        except ProtectedError:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این موتورسیکلت به "
                        "اطلاعات دیگری وابسته "
                        "است و قابل حذف نیست."
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
                    "موتورسیکلت با موفقیت "
                    "حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )