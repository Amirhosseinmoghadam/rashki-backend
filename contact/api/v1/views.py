from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema, extend_schema_view,
)

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from contact.models import ContactRequest
from .serializers import (
    ContactRequestAdminSerializer,
    ContactRequestCreateSerializer,
)
from contact.throttles import ContactRequestThrottle





from contact.api.v1.openapi.schema import (
    contact_create_view_schema,
    contact_admin_list_view_schema,
    contact_admin_detail_view_schema,
    contact_admin_partial_update_view_schema,
)

@extend_schema_view(
    post=contact_create_view_schema,
)
class ContactRequestCreateAPIView(
    generics.CreateAPIView
):
    """
    ثبت درخواست تماس توسط کاربر.
    """

    queryset = ContactRequest.objects.all()

    serializer_class = ContactRequestCreateSerializer

    permission_classes = [
        AllowAny,
    ]

    authentication_classes = []

    throttle_classes = [
        ContactRequestThrottle,
    ]

    @extend_schema(
        tags=["Contact"],
        summary="ثبت درخواست تماس با ما",
        description=(
            "ثبت درخواست تماس توسط کاربران. "
            "برای ثبت درخواست نیازی به ورود به حساب کاربری نیست."
        ),
        request=ContactRequestCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="درخواست با موفقیت ثبت شد."
            ),
            400: OpenApiResponse(
                description="اطلاعات ارسال شده معتبر نیست."
            ),
            429: OpenApiResponse(
                description=(
                    "تعداد درخواست‌ها بیش از حد مجاز است."
                )
            ),
        },
        examples=[
            OpenApiExample(
                "استعلام قیمت",
                value={
                    "first_name": "امیرحسین",
                    "last_name": "مقدم",
                    "phone_number": "09123456789",
                    "subject": "price_inquiry",
                    "description": (
                        "سلام، لطفاً قیمت عمده این محصول "
                        "را اعلام کنید."
                    ),
                },
                request_only=True,
            ),
            OpenApiExample(
                "درخواست همکاری عمده",
                value={
                    "first_name": "علی",
                    "last_name": "رضایی",
                    "phone_number": "09123456789",
                    "subject": "wholesale_cooperation",
                    "description": (
                        "برای همکاری در زمینه خرید عمده "
                        "لوازم یدکی موتور سیکلت تماس می‌گیرم."
                    ),
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        contact_request = serializer.save()

        return Response(
            {
                "message": "درخواست شما با موفقیت ثبت شد.",
                "data": {
                    "id": contact_request.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    get=contact_admin_list_view_schema,
)
class ContactRequestListAPIView(
    generics.ListAPIView
):
    """
    مشاهده درخواست‌های تماس توسط ادمین.
    """

    queryset = ContactRequest.objects.all()

    serializer_class = ContactRequestAdminSerializer

    permission_classes = [
        IsAdminUser,
    ]

    @extend_schema(
        tags=["Contact"],
        summary="لیست درخواست‌های تماس",
        description=(
            "فقط کاربران Staff/Admin می‌توانند "
            "درخواست‌های تماس را مشاهده کنند."
        ),
        responses=ContactRequestAdminSerializer(
            many=True
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request,
            *args,
            **kwargs,
        )

@extend_schema_view(
    get=contact_admin_detail_view_schema,
    patch=contact_admin_partial_update_view_schema,
)
class ContactRequestDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    """
    مشاهده و تغییر وضعیت درخواست توسط ادمین.
    """

    queryset = ContactRequest.objects.all()

    serializer_class = ContactRequestAdminSerializer

    permission_classes = [
        IsAdminUser,
    ]

    @extend_schema(
        tags=["Contact"],
        summary="مشاهده جزئیات درخواست تماس",
        description=(
            "مشاهده یک درخواست تماس توسط ادمین."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request,
            *args,
            **kwargs,
        )

    @extend_schema(
        tags=["Contact"],
        summary="تغییر وضعیت درخواست",
        description=(
            "ادمین می‌تواند وضعیت خوانده شدن "
            "درخواست را تغییر دهد."
        ),
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(
            request,
            *args,
            **kwargs,
        )