from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from utils.pagination import DefaultPagination
from wishlists.models import WishlistItem
from wishlists.selectors import (
    get_public_products_queryset,
    get_user_wishlist_queryset,
)


from .serializers import (
    WishlistItemSerializer,
)

from .openapi.schema import (
    wishlist_list_view_schema,
    wishlist_add_view_schema,
    wishlist_remove_view_schema,
    wishlist_product_ids_view_schema,
)


# =========================================================
# Wishlist List
# =========================================================


class WishlistListAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        WishlistItemSerializer
    )

    pagination_class = (
        DefaultPagination
    )

    # =====================================================
    # QuerySet
    # =====================================================

    def get_queryset(self):

        return (
            get_user_wishlist_queryset(
                self.request.user
            )
        )

    # =====================================================
    # GET
    # =====================================================

    @wishlist_list_view_schema
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = (
            self.get_queryset()
        )

        page = self.paginate_queryset(
            queryset
        )

        serializer = (
            self.get_serializer(
                page,
                many=True,
            )
        )

        pagination_data = (
            self.get_paginated_response(
                serializer.data
            ).data
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست علاقه‌مندی‌ها "
                    "با موفقیت دریافت شد."
                ),
                "data": pagination_data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Wishlist Add / Remove
# =========================================================


class WishlistItemAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        WishlistItemSerializer
    )

    # =====================================================
    # POST - Add
    # =====================================================

    @wishlist_add_view_schema
    def post(
        self,
        request,
        product_id,
        *args,
        **kwargs,
    ):

        # فقط Product عمومی و Active
        # قابل افزودن به Wishlist است.
        product = (
            get_public_products_queryset()
            .select_related(
                "category",
                "brand",
            )
            .filter(
                pk=product_id
            )
            .first()
        )

        if product is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "محصول موردنظر یافت نشد "
                        "یا در حال حاضر قابل "
                        "نمایش نیست."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        # UniqueConstraint تضمین می‌کند
        # یک Product دوبار برای User ثبت نشود.
        wishlist_item, created = (
            WishlistItem.objects
            .get_or_create(
                user=request.user,
                product=product,
            )
        )

        # برای Response بهینه،
        # Item را دوباره از selector می‌گیریم
        # تا Primary Image Prefetch شده باشد.
        wishlist_item = (
            get_user_wishlist_queryset(
                request.user
            )
            .filter(
                pk=wishlist_item.pk
            )
            .first()
        )

        serializer = (
            self.get_serializer(
                wishlist_item
            )
        )

        # اگر قبلاً وجود داشته باشد،
        # POST همچنان Idempotent رفتار می‌کند.
        if created:

            message = (
                "محصول با موفقیت به "
                "علاقه‌مندی‌ها اضافه شد."
            )

            response_status = (
                status.HTTP_201_CREATED
            )

        else:

            message = (
                "این محصول از قبل در "
                "علاقه‌مندی‌های شما وجود دارد."
            )

            response_status = (
                status.HTTP_200_OK
            )

        return Response(
            {
                "success": True,
                "message": message,
                "data": serializer.data,
            },
            status=response_status,
        )

    # =====================================================
    # DELETE - Remove
    # =====================================================

    @wishlist_remove_view_schema
    def delete(
        self,
        request,
        product_id,
        *args,
        **kwargs,
    ):

        wishlist_item = (
            WishlistItem.objects
            .filter(
                user=request.user,
                product_id=product_id,
            )
            .first()
        )

        if wishlist_item is None:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این محصول در "
                        "علاقه‌مندی‌های شما "
                        "وجود ندارد."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        wishlist_item.delete()

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت از "
                    "علاقه‌مندی‌ها حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Wishlist Product IDs
# =========================================================


class WishlistProductIdsAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    # =====================================================
    # GET
    # =====================================================

    @wishlist_product_ids_view_schema
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):

        product_ids = list(
            get_user_wishlist_queryset(
                request.user
            )
            .values_list(
                "product_id",
                flat=True,
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "شناسه محصولات مورد علاقه "
                    "با موفقیت دریافت شد."
                ),
                "count": len(
                    product_ids
                ),
                "data": product_ids,
            },
            status=status.HTTP_200_OK,
        )