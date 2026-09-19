from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from addresses.selectors import (
    get_cities_for_province,
    get_provinces,
    get_user_address,
    get_user_addresses,
)
from addresses.services import (
    delete_address,
    set_default_address,
)

from .openapi.schema import (
    address_create_view_schema,
    address_delete_view_schema,
    address_detail_view_schema,
    address_list_view_schema,
    address_partial_update_view_schema,
    address_set_default_view_schema,
    address_update_view_schema,
    city_list_view_schema,
    province_list_view_schema,
)
from .serializers import (
    AddressCreateSerializer,
    AddressSerializer,
    AddressUpdateSerializer,
    CitySerializer,
    ProvinceSerializer,
)


class ProvinceListView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProvinceSerializer
    pagination_class = None

    @province_list_view_schema
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            get_provinces(),
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست استان‌ها با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CityListView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    pagination_class = None

    @city_list_view_schema
    def get(
        self,
        request,
        province_id,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(
            get_cities_for_province(
                province_id=province_id,
            ),
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست شهرها با موفقیت دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AddressListCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddressCreateSerializer

        return AddressSerializer

    @address_list_view_schema
    def get(self, request, *args, **kwargs):
        serializer = AddressSerializer(
            get_user_addresses(
                user=request.user,
            ),
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        address = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت ایجاد شد."
                ),
                "data": AddressSerializer(
                    address,
                    context={
                        "request": request,
                    },
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AddressDetailAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressUpdateSerializer

    def _get_address(self, *, request, pk):
        return get_user_address(
            user=request.user,
            pk=pk,
        )

    @address_detail_view_schema
    def get(self, request, pk, *args, **kwargs):
        address = self._get_address(
            request=request,
            pk=pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": (
                        "آدرس موردنظر پیدا نشد."
                    ),
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت دریافت شد."
                ),
                "data": AddressSerializer(
                    address,
                    context={
                        "request": request,
                    },
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @address_update_view_schema
    def put(self, request, pk, *args, **kwargs):
        return self._update(
            request=request,
            pk=pk,
            partial=False,
        )

    @address_partial_update_view_schema
    def patch(self, request, pk, *args, **kwargs):
        return self._update(
            request=request,
            pk=pk,
            partial=True,
        )

    def _update(
        self,
        *,
        request,
        pk,
        partial,
    ):
        address = self._get_address(
            request=request,
            pk=pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": (
                        "آدرس موردنظر پیدا نشد."
                    ),
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
            raise_exception=True,
        )

        address = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس با موفقیت بروزرسانی شد."
                ),
                "data": AddressSerializer(
                    address,
                    context={
                        "request": request,
                    },
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @address_delete_view_schema
    def delete(self, request, pk, *args, **kwargs):
        address = self._get_address(
            request=request,
            pk=pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": (
                        "آدرس موردنظر پیدا نشد."
                    ),
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        delete_address(
            address=address,
        )

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


class AddressSetDefaultAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    @address_set_default_view_schema
    def post(self, request, pk, *args, **kwargs):
        address = get_user_address(
            user=request.user,
            pk=pk,
        )

        if address is None:
            return Response(
                {
                    "success": False,
                    "message": (
                        "آدرس موردنظر پیدا نشد."
                    ),
                    "errors": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        address = set_default_address(
            address=address,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "آدرس پیش‌فرض با موفقیت تغییر کرد."
                ),
                "data": AddressSerializer(
                    address,
                    context={
                        "request": request,
                    },
                ).data,
            },
            status=status.HTTP_200_OK,
        )
