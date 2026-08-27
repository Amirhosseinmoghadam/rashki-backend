from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from django.shortcuts import get_object_or_404

from carts.models import Cart, CartItem
from products.models import ProductVariant

from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)

from .openapi.schema import (
    cart_list_view_schema,

    add_to_cart_view_schema,
    update_cart_item_view_schema,
    remove_cart_item_view_schema,
    clear_cart_view_schema,
)


# =========================================================
# Cart List API View
# =========================================================
@cart_list_view_schema
class CartListView(APIView):
    """
    Get the authenticated user's cart with all items.

    Returns the current cart with all items, quantities, and calculated totals.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get or create cart for the user
        cart, created = Cart.objects.get_or_create(
            user=request.user,
        )

        serializer = CartSerializer(cart)

        return Response(
            {
                "message": "سبد خرید با موفقیت دریافت شد.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Add to Cart API View
# =========================================================
@add_to_cart_view_schema
class AddToCartView(APIView):
    """
    Add a product variant to the user's cart.

    If the variant already exists in the cart, the quantity will be increased.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant_id = serializer.validated_data["variant_id"]
        quantity = serializer.validated_data["quantity"]

        # Get or create cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Get variant
        variant = get_object_or_404(ProductVariant, pk=variant_id)

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity},
        )

        if not created:
            # Item exists, update quantity
            cart_item.quantity += quantity
            cart_item.save(update_fields=["quantity"])

        # Serialize and return updated cart
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)

        return Response(
            {
                "message": "محصول با موفقیت به سبد خرید اضافه شد.",
                "data": cart_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Update Cart Item API View
# =========================================================
@update_cart_item_view_schema
class UpdateCartItemView(APIView):
    """
    Update the quantity of a specific item in the cart.

    This allows setting a new quantity for an existing cart item.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, item_id):
        # Get cart item and ensure it belongs to user's cart
        cart_item = get_object_or_404(
            CartItem.objects.select_related("cart"),
            pk=item_id,
            cart__user=request.user,
        )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]

        # Update quantity
        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity", "updated_at"])

        # Serialize and return updated cart
        cart_item.cart.refresh_from_db()
        cart_serializer = CartSerializer(cart_item.cart)

        return Response(
            {
                "message": "تعداد محصول با موفقیت بروزرسانی شد.",
                "data": cart_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, item_id):
        return self.put(request, item_id)


# =========================================================
# Remove Cart Item API View
# =========================================================
@remove_cart_item_view_schema
class RemoveCartItemView(APIView):
    """
    Remove a specific item from the cart.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, item_id):
        # Get cart item and ensure it belongs to user's cart
        cart_item = get_object_or_404(
            CartItem,
            pk=item_id,
            cart__user=request.user,
        )

        cart_item.delete()

        # Serialize and return updated cart
        cart_item.cart.refresh_from_db()
        cart_serializer = CartSerializer(cart_item.cart)

        return Response(
            {
                "message": "محصول با موفقیت از سبد خرید حذف شد.",
                "data": cart_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Clear Cart API View
# =========================================================
@clear_cart_view_schema
class ClearCartView(APIView):
    """
    Remove all items from the user's cart.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        # Get user's cart
        cart = get_object_or_404(Cart, user=request.user)

        # Delete all items
        cart.items.all().delete()

        # Serialize empty cart
        cart.refresh_from_db()
        cart_serializer = CartSerializer(cart)

        return Response(
            {
                "message": "سبد خرید با موفقیت خالی شد.",
                "data": cart_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

