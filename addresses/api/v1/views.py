from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from addresses.api.v1.serializers import AddressSerializer
from addresses.models import Province, City, Address
from addresses.api.v1.serializers import ProvinceSerializer, CitySerializer
from drf_spectacular.utils import extend_schema

from .serializers import (

    AddressCreateSerializer,
    AddressSerializer,
    AddressUpdateSerializer,
)


from addresses.api.v1.openapi.schema import (
    address_list_view_schema,
    address_create_view_schema,
    address_detail_view_schema,
    address_update_view_schema,
    address_partial_update_view_schema,
    address_delete_view_schema,
    address_set_default_view_schema,
)


from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

@extend_schema(tags=["Locations"])
class ProvinceListView(ListAPIView):
    """
    API View to provide a list of all Provinces.
    Returns 'id' and 'name' for each province.
    Accessible by any user (AllowAny).
    """

    queryset = Province.objects.all().order_by("name")
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]
    pagination_class = None


@extend_schema(tags=["Locations"])
class CityListView(ListAPIView):
    """
    API View to provide a list of Cities filtered by a specific Province ID.
    The Province ID is expected as part of the URL (e.g., /provinces/<province_id>/cities/).
    Returns 'id' and 'name' for each city within that province.
    Accessible by any user (AllowAny).
    """

    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        """
        Overrides the default queryset behavior to filter cities
        based on the 'province_id' captured from the URL.
        """
        province_id = self.kwargs.get("province_id")
        if province_id is not None:
            return City.objects.filter(province_id=province_id).order_by("name")
        return City.objects.none()




# =========================================================
# AddressListCreateAPIView
# =========================================================
class AddressListCreateAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self, user):
        return (
            Address.objects
            .filter(user=user)
            .select_related(
                "province",
                "city",
            )
            .order_by(
                "-is_default",
                "-created_at",
            )
        )

    @address_list_view_schema
    def get(self, request):
        addresses = self.get_queryset(
            request.user
        )

        serializer = AddressSerializer(
            addresses,
            many=True,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست آدرس‌ها با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_create_view_schema
    def post(self, request):
        serializer = AddressCreateSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت ایجاد شد."
                ),
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# AddressDetailAPIView
# =========================================================
class AddressDetailAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, request, pk):
        return (
            Address.objects
            .filter(
                pk=pk,
                user=request.user,
            )
            .select_related(
                "province",
                "city",
            )
            .first()
        )

    @address_detail_view_schema
    def get(self, request, pk):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_update_view_schema
    @transaction.atomic
    def put(self, request, pk):
        return self._update(
            request,
            pk,
            partial=False,
        )

    @address_partial_update_view_schema
    @transaction.atomic
    def patch(self, request, pk):
        return self._update(
            request,
            pk,
            partial=True,
        )

    def _update(
        self,
        request,
        pk,
        partial=False,
    ):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AddressUpdateSerializer(
            address,
            data=request.data,
            partial=partial,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        address = serializer.save()

        response_serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت بروزرسانی شد."
                ),
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @address_delete_view_schema
    @transaction.atomic
    def delete(self, request, pk):
        address = self.get_object(
            request,
            pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        was_default = address.is_default

        address.delete()

        # اگر آدرس پیش‌فرض حذف شد،
        # یک آدرس دیگر را پیش‌فرض کن.
        if was_default:
            new_default = (
                Address.objects
                .filter(
                    user=request.user
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )

            if new_default:
                new_default.set_as_default()

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# AddressSetDefaultAPIView
# =========================================================
class AddressSetDefaultAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @address_set_default_view_schema
    @transaction.atomic
    def post(self, request, pk):
        address = (
            Address.objects
            .select_for_update()
            .filter(
                pk=pk,
                user=request.user,
            )
            .first()
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": "آدرس موردنظر پیدا نشد.",
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # همه آدرس‌های قبلی غیرپیش‌فرض شوند
        (
            Address.objects
            .filter(
                user=request.user,
                is_default=True,
            )
            .exclude(
                pk=address.pk
            )
            .update(
                is_default=False
            )
        )

        address.is_default = True

        address.save(
            update_fields=[
                "is_default",
                "updated_at",
            ]
        )

        serializer = AddressSerializer(
            address,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس پیش‌فرض با موفقیت تغییر کرد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

