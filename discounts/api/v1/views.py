from django.db.models import (
    Count,
    Q,
)
from django.db.models.deletion import (
    ProtectedError,
)

from rest_framework import (
    generics,
    status,
    viewsets,
)

from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)

from rest_framework.response import Response

from discounts.models import (
    DiscountCode,
    DiscountUsage,
)

from discounts.selectors import (
    get_discount_products_queryset,
)

from discounts.services import (
    DiscountLine,
    DiscountValidationError,
    calculate_discount,
    get_discount_by_code,
)

from .serializers import (
    DiscountCodeSerializer,
    DiscountValidateSerializer,
)

from .openapi.schema import (
    discount_list_view_schema,
    discount_detail_view_schema,
    discount_create_view_schema,
    discount_update_view_schema,
    discount_partial_update_view_schema,
    discount_delete_view_schema,
    discount_validate_view_schema,
)


# =========================================================
# Admin Discount CRUD
# =========================================================


class DiscountCodeViewSet(
    viewsets.ModelViewSet
):

    permission_classes = [
        IsAdminUser,
    ]

    serializer_class = (
        DiscountCodeSerializer
    )

    pagination_class = None

    def get_queryset(self):

        return (
            DiscountCode.objects
            .prefetch_related(
                "products",
                "categories",
            )
            .annotate(
                active_usage_count=Count(
                    "usages",
                    filter=Q(
                        usages__status=(
                            DiscountUsage
                            .Status
                            .USED
                        )
                    ),
                )
            )
            .order_by(
                "-created_at"
            )
        )

    # =====================================================
    # List
    # =====================================================

    @discount_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = (
            self.get_queryset()
        )

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست کدهای تخفیف "
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
    # Detail
    # =====================================================

    @discount_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        discount = self.get_object()

        serializer = self.get_serializer(
            discount
        )

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # Create
    # =====================================================

    @discount_create_view_schema
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

        discount = serializer.save()

        response_serializer = (
            self.get_serializer(
                discount
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف با موفقیت "
                    "ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # Update
    # =====================================================

    @discount_update_view_schema
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

        discount = self.get_object()

        serializer = self.get_serializer(
            discount,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        discount = serializer.save()

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف با موفقیت "
                    "بروزرسانی شد."
                ),
                "data": (
                    self.get_serializer(
                        discount
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PATCH
    # =====================================================

    @discount_partial_update_view_schema
    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):

        kwargs[
            "partial"
        ] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # Delete
    # =====================================================

    @discount_delete_view_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        discount = self.get_object()

        try:

            discount.delete()

        except ProtectedError:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این کد دارای سابقه "
                        "استفاده است و قابل "
                        "حذف نیست. آن را "
                        "غیرفعال کنید."
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
                    "کد تخفیف با موفقیت "
                    "حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Validate Discount
# =========================================================


class DiscountValidateAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        DiscountValidateSerializer
    )

    @discount_validate_view_schema
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

        code = serializer.validated_data[
            "code"
        ]

        items = serializer.validated_data[
            "items"
        ]

        try:

            discount = get_discount_by_code(
                code
            )

            product_ids = [
                item[
                    "product_id"
                ]
                for item in items
            ]

            products = {
                product.id: product
                for product
                in get_discount_products_queryset()
                .filter(
                    id__in=product_ids
                )
            }

            missing_ids = (
                set(product_ids)
                - set(products.keys())
            )

            if missing_ids:

                raise DiscountValidationError(
                    "یک یا چند محصول سبد "
                    "در حال حاضر قابل خرید نیستند."
                )

            lines = []

            for item in items:

                product = products[
                    item["product_id"]
                ]

                lines.append(
                    DiscountLine(
                        product=product,
                        quantity=(
                            item["quantity"]
                        ),
                        unit_price_toman=(
                            product
                            .current_price_toman
                        ),
                    )
                )

            result = calculate_discount(
                discount=discount,
                lines=lines,
                user=request.user,
            )

        except DiscountValidationError as exc:

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

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف معتبر است."
                ),
                "data": {
                    "code": discount.code,
                    "discount_type": (
                        discount.discount_type
                    ),
                    "scope": discount.scope,
                    "subtotal_toman": (
                        result.subtotal_toman
                    ),
                    "eligible_subtotal_toman": (
                        result
                        .eligible_subtotal_toman
                    ),
                    "discount_amount_toman": (
                        result
                        .discount_amount_toman
                    ),
                    "final_subtotal_toman": (
                        result
                        .final_subtotal_toman
                    ),
                    "start_at": (
                        discount.start_at
                    ),
                    "end_at": (
                        discount.end_at
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )