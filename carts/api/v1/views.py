from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import (
    Response,
)

from discounts.services import (
    DiscountValidationError,
)

from carts.services import (
    CartItemNotFoundError,
    CartValidationError,
    add_cart_item,
    apply_cart_discount,
    calculate_cart,
    clear_cart,
    get_cart,
    remove_cart_discount,
    remove_cart_item,
    update_cart_item,
)

from .serializers import (
    CartSerializer,
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    CartDiscountApplySerializer,
)

from .openapi.schema import (
    cart_detail_view_schema,
    cart_add_item_view_schema,
    cart_update_item_view_schema,
    cart_remove_item_view_schema,
    cart_clear_view_schema,
    cart_apply_discount_view_schema,
    cart_remove_discount_view_schema,
)


# =========================================================
# Cart Detail
# =========================================================


class CartAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        CartSerializer
    )

    @cart_detail_view_schema
    def get(
        self,
        request,
        *args,
        **kwargs,
    ):

        cart = get_cart(
            request.user
        )

        data = calculate_cart(
            cart
        )

        serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "سبد خرید با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Add Cart Item
# =========================================================


class CartItemAddAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        CartItemAddSerializer
    )

    @cart_add_item_view_schema
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
                cart,
                created,
            ) = add_cart_item(
                user=request.user,
                product_id=(
                    serializer
                    .validated_data[
                        "product_id"
                    ]
                ),
                quantity=(
                    serializer
                    .validated_data[
                        "quantity"
                    ]
                ),
            )

            data = calculate_cart(
                cart
            )

        except CartValidationError as exc:

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

        response_serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت به "
                    "سبد خرید اضافه شد."
                    if created
                    else
                    "تعداد محصول در سبد "
                    "خرید بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )


# =========================================================
# Update / Remove Item
# =========================================================


class CartItemAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        CartItemUpdateSerializer
    )

    # =====================================================
    # PATCH
    # =====================================================

    @cart_update_item_view_schema
    def patch(
        self,
        request,
        product_id,
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

            cart = update_cart_item(
                user=request.user,
                product_id=product_id,
                quantity=(
                    serializer
                    .validated_data[
                        "quantity"
                    ]
                ),
            )

            data = calculate_cart(
                cart
            )

        except CartItemNotFoundError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        except CartValidationError as exc:

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

        response_serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "تعداد محصول با موفقیت "
                    "بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # DELETE
    # =====================================================

    @cart_remove_item_view_schema
    def delete(
        self,
        request,
        product_id,
        *args,
        **kwargs,
    ):

        try:

            cart = remove_cart_item(
                user=request.user,
                product_id=product_id,
            )

            data = calculate_cart(
                cart
            )

        except CartItemNotFoundError as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": None,
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت از "
                    "سبد خرید حذف شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Clear Cart
# =========================================================


class CartClearAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    @cart_clear_view_schema
    def delete(
        self,
        request,
        *args,
        **kwargs,
    ):

        cart = clear_cart(
            request.user
        )

        data = calculate_cart(
            cart
        )

        serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "سبد خرید با موفقیت "
                    "خالی شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Cart Discount
# =========================================================


class CartDiscountAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = (
        CartDiscountApplySerializer
    )

    # =====================================================
    # POST
    # =====================================================

    @cart_apply_discount_view_schema
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

            cart = apply_cart_discount(
                user=request.user,
                code=(
                    serializer
                    .validated_data[
                        "code"
                    ]
                ),
            )

            data = calculate_cart(
                cart
            )

        except (
            CartValidationError,
            DiscountValidationError,
        ) as exc:

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

        response_serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف با موفقیت "
                    "روی سبد خرید اعمال شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # DELETE
    # =====================================================

    @cart_remove_discount_view_schema
    def delete(
        self,
        request,
        *args,
        **kwargs,
    ):

        cart = remove_cart_discount(
            request.user
        )

        data = calculate_cart(
            cart
        )

        serializer = CartSerializer(
            data,
            context={
                "request": request,
            },
        )

        return Response(
            {
                "success": True,
                "message": (
                    "کد تخفیف از سبد "
                    "خرید حذف شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )