from rest_framework import (
    generics,
    status,
    viewsets,
)

from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)

from rest_framework.response import Response

from shipping.models import (
    ShippingMethod,
    ShippingRateRule,
)

from shipping.services import (
    ShippingValidationError,
    get_shipping_quotes,
)

from .serializers import (
    ShippingMethodSerializer,
    ShippingQuoteRequestSerializer,
    ShippingQuoteSerializer,
    ShippingRateRuleSerializer,
)

from .openapi.schema import (
    shipping_method_list_schema,
    shipping_method_detail_schema,
    shipping_method_create_schema,
    shipping_method_update_schema,
    shipping_method_partial_update_schema,
    shipping_method_delete_schema,

    shipping_rate_list_schema,
    shipping_rate_detail_schema,
    shipping_rate_create_schema,
    shipping_rate_update_schema,
    shipping_rate_partial_update_schema,
    shipping_rate_delete_schema,

    shipping_quote_schema,
)


# =========================================================
# Shipping Method
# =========================================================


class ShippingMethodViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        ShippingMethodSerializer
    )

    pagination_class = None

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

    def get_queryset(self):

        queryset = (
            ShippingMethod.objects.all()
        )

        if self.action in {
            "list",
            "retrieve",
        }:

            queryset = queryset.filter(
                is_active=True
            )

        return queryset.order_by(
            "sort_order",
            "id",
        )

    @shipping_method_list_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "روش‌های ارسال با موفقیت "
                    "دریافت شدند."
                ),
                "count": len(
                    serializer.data
                ),
                "data": serializer.data,
            }
        )

    @shipping_method_detail_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        obj = self.get_object()

        return Response(
            {
                "success": True,
                "message": (
                    "روش ارسال با موفقیت "
                    "دریافت شد."
                ),
                "data": (
                    self.get_serializer(
                        obj
                    ).data
                ),
            }
        )

    @shipping_method_create_schema
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

        obj = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "روش ارسال با موفقیت "
                    "ایجاد شد."
                ),
                "data": (
                    self.get_serializer(
                        obj
                    ).data
                ),
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )

    @shipping_method_update_schema
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

        obj = self.get_object()

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        obj = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "روش ارسال بروزرسانی شد."
                ),
                "data": (
                    self.get_serializer(
                        obj
                    ).data
                ),
            }
        )

    @shipping_method_partial_update_schema
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

    @shipping_method_delete_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        self.get_object().delete()

        return Response(
            {
                "success": True,
                "message": (
                    "روش ارسال حذف شد."
                ),
                "data": None,
            }
        )


# =========================================================
# Shipping Rate Admin API
# =========================================================


class ShippingRateRuleViewSet(
    viewsets.ModelViewSet
):

    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = (
        ShippingRateRuleSerializer
    )

    pagination_class = None

    queryset = (
        ShippingRateRule.objects
        .select_related(
            "method",
            "province",
            "city",
        )
        .order_by(
            "-priority",
            "-effective_from",
        )
    )

    @shipping_rate_list_schema
    def list(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            self.get_queryset(),
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "تعرفه‌های ارسال دریافت شدند."
                ),
                "count": len(serializer.data),
                "data": serializer.data,
            }
        )

    @shipping_rate_detail_schema
    def retrieve(self, request, *args, **kwargs):

        obj = self.get_object()

        return Response(
            {
                "success": True,
                "message": "تعرفه ارسال دریافت شد.",
                "data": self.get_serializer(
                    obj
                ).data,
            }
        )

    @shipping_rate_create_schema
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        obj = serializer.save()

        return Response(
            {
                "success": True,
                "message": "تعرفه ارسال ایجاد شد.",
                "data": self.get_serializer(
                    obj
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @shipping_rate_update_schema
    def update(self, request, *args, **kwargs):

        partial = kwargs.pop(
            "partial",
            False,
        )

        obj = self.get_object()

        serializer = self.get_serializer(
            obj,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        obj = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "تعرفه ارسال بروزرسانی شد."
                ),
                "data": self.get_serializer(
                    obj
                ).data,
            }
        )

    @shipping_rate_partial_update_schema
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

    @shipping_rate_delete_schema
    def destroy(self, request, *args, **kwargs):

        self.get_object().delete()

        return Response(
            {
                "success": True,
                "message": "تعرفه ارسال حذف شد.",
                "data": None,
            }
        )


# =========================================================
# Shipping Quote
# =========================================================


class ShippingQuoteAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        ShippingQuoteRequestSerializer
    )

    @shipping_quote_schema
    def post(
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

        try:

            (
                address,
                weight,
                quotes,
            ) = get_shipping_quotes(
                user=request.user,
                address_id=(
                    serializer
                    .validated_data[
                        "address_id"
                    ]
                ),
            )

        except ShippingValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": None,
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        quote_serializer = (
            ShippingQuoteSerializer(
                quotes,
                many=True,
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "هزینه روش‌های ارسال "
                    "با موفقیت محاسبه شد."
                ),
                "data": {
                    "address_id": address.id,
                    "province": (
                        address.province.name
                    ),
                    "city": address.city.name,
                    "weight_grams": weight,
                    "quotes": (
                        quote_serializer.data
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )