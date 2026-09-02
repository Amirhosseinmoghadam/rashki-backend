from drf_spectacular.utils import extend_schema_view

from rest_framework import (
    generics,
    status,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
)
from rest_framework.response import Response

from contact.models import ContactRequest
from contact.throttles import (
    ContactRequestThrottle,
)

from utils.pagination import DefaultPagination

from .serializers import (
    ContactRequestCreateSerializer,
    ContactRequestAdminSerializer,
    ContactRequestStatusSerializer,
)

from .openapi.schema import (
    contact_create_view_schema,
    contact_admin_list_view_schema,
    contact_admin_detail_view_schema,
    contact_admin_partial_update_view_schema,
)


# =========================================================
# Contact Create
# =========================================================


@extend_schema_view(
    post=contact_create_view_schema,
)
class ContactRequestCreateAPIView(
    generics.CreateAPIView
):
    """
    Public endpoint for creating
    a contact request.
    """

    queryset = (
        ContactRequest.objects.all()
    )

    serializer_class = (
        ContactRequestCreateSerializer
    )

    permission_classes = [
        AllowAny,
    ]

    # Public endpoint.
    # Authentication is intentionally disabled here.
    authentication_classes = []

    throttle_classes = [
        ContactRequestThrottle,
    ]

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        contact_request = (
            serializer.save()
        )

        return Response(
            {
                "success": True,
                "message": (
                    "درخواست شما با موفقیت "
                    "ثبت شد."
                ),
                "data": {
                    "id": contact_request.id,
                },
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )


# =========================================================
# Contact Admin List
# =========================================================


@extend_schema_view(
    get=contact_admin_list_view_schema,
)
class ContactRequestListAPIView(
    generics.ListAPIView
):
    """
    List contact requests.

    Admin only.
    """

    queryset = (
        ContactRequest.objects.all()
        .order_by(
            "-created_at"
        )
    )

    serializer_class = (
        ContactRequestAdminSerializer
    )

    permission_classes = [
        IsAdminUser,
    ]

    pagination_class = (
        DefaultPagination
    )

    # =====================================================
    # LIST
    # =====================================================

    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = (
            self.filter_queryset(
                self.get_queryset()
            )
        )

        page = (
            self.paginate_queryset(
                queryset
            )
        )

        if page is not None:

            serializer = self.get_serializer(
                page,
                many=True,
            )

            paginated_response = (
                self.get_paginated_response(
                    serializer.data
                )
            )

            return Response(
                {
                    "success": True,
                    "message": (
                        "لیست درخواست‌های تماس "
                        "با موفقیت دریافت شد."
                    ),
                    "data": (
                        paginated_response.data
                    ),
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست درخواست‌های تماس "
                    "با موفقیت دریافت شد."
                ),
                "data": {
                    "count": len(
                        serializer.data
                    ),
                    "next": None,
                    "previous": None,
                    "results": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Contact Admin Detail
# =========================================================


class ContactRequestDetailAPIView(
    generics.GenericAPIView
):
    """
    Admin contact request endpoint.

    Supported:
        GET
        PATCH

    PUT is intentionally not available.
    """

    queryset = (
        ContactRequest.objects.all()
    )

    permission_classes = [
        IsAdminUser,
    ]

    # =====================================================
    # Serializer
    # =====================================================

    def get_serializer_class(self):

        if self.request.method == "PATCH":

            return (
                ContactRequestStatusSerializer
            )

        return (
            ContactRequestAdminSerializer
        )

    # =====================================================
    # Object
    # =====================================================

    def get_object(self):

        pk = self.kwargs.get(
            "pk"
        )

        contact_request = (
            ContactRequest.objects
            .filter(
                pk=pk
            )
            .first()
        )

        if contact_request is None:

            raise NotFound(
                "درخواست تماس موردنظر "
                "پیدا نشد."
            )

        self.check_object_permissions(
            self.request,
            contact_request,
        )

        return contact_request

    # =====================================================
    # GET
    # =====================================================

    @contact_admin_detail_view_schema
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):

        contact_request = (
            self.get_object()
        )

        serializer = (
            ContactRequestAdminSerializer(
                contact_request,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "درخواست تماس با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PATCH
    # =====================================================

    @contact_admin_partial_update_view_schema
    def patch(
        self,
        request,
        *args,
        **kwargs,
    ):

        contact_request = (
            self.get_object()
        )

        serializer = (
            ContactRequestStatusSerializer(
                contact_request,
                data=request.data,
                partial=True,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        contact_request = (
            serializer.save()
        )

        response_serializer = (
            ContactRequestAdminSerializer(
                contact_request,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "وضعیت درخواست تماس "
                    "با موفقیت بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )