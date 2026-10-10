from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import OperationalError, connections, transaction
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature
from django.utils import timezone

from carts.models import Cart, CartItem
from carts.services import update_cart_item
from categories.models import Category
from orders.models import Order, OrderItem
from orders.services import (
    InvalidOrderTransitionError,
    OrderValidationError,
    cancel_unpaid_order,
    create_order_from_cart,
)
from products.models import Product


def create_product():
    category = Category.objects.create(name="Lock test", slug="lock-test")
    return Product.objects.create(
        name="Lock test product",
        slug="lock-test-product",
        sku="LOCK-001",
        category=category,
        brand=None,
        current_price_toman=100_000,
        stock_quantity=9,
        status=Product.Status.ACTIVE,
    )


class NullableJoinLockTests(TestCase):
    """These service calls must also work with PostgreSQL's FOR UPDATE."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(phone_number="09120000001")
        self.cart = Cart.objects.create(user=self.user)

    def test_checkout_without_discount_reaches_empty_cart_validation(self):
        with self.assertRaisesMessage(OrderValidationError, "سبد خرید خالی است."):
            create_order_from_cart(
                user=self.user,
                address_id=0,
                shipping_method_id=0,
                accept_terms=True,
            )

    def test_cart_item_without_brand_can_be_updated(self):
        product = create_product()
        item = CartItem.objects.create(cart=self.cart, product=product, quantity=1)
        update_cart_item(user=self.user, product_id=product.pk, quantity=2)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_checkout_without_brand_reaches_stock_validation(self):
        product = create_product()
        CartItem.objects.create(cart=self.cart, product=product, quantity=10)
        with self.assertRaisesMessage(OrderValidationError, "کافی نیست"):
            create_order_from_cart(
                user=self.user,
                address_id=0,
                shipping_method_id=0,
                accept_terms=True,
            )


@skipUnlessDBFeature("has_select_for_update", "has_select_for_update_nowait")
class PostgreSQLRowLockTests(TransactionTestCase):
    """Real commits and separate thread-local database connections are required."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(phone_number="09120000002")
        self.product = create_product()

    @staticmethod
    def try_product_lock(product_id):
        try:
            with transaction.atomic():
                # Bound the worker even if locking behavior changes.
                with connections["default"].cursor() as cursor:
                    cursor.execute("SET LOCAL lock_timeout = '5s'")
                return (
                    Product.objects.select_for_update(nowait=True)
                    .get(pk=product_id)
                    .stock_quantity
                )
        finally:
            connections.close_all()

    def test_product_lock_rejects_other_connection_until_commit(self):
        with ThreadPoolExecutor(max_workers=1) as pool:
            with transaction.atomic():
                Product.objects.select_for_update(of=("self",)).select_related(
                    "category", "brand"
                ).get(pk=self.product.pk)
                future = pool.submit(self.try_product_lock, self.product.pk)
                with self.assertRaises(OperationalError) as error:
                    future.result(timeout=10)
                cause = error.exception.__cause__
                self.assertEqual(getattr(cause, "sqlstate", None), "55P03")

            self.assertEqual(
                pool.submit(self.try_product_lock, self.product.pk).result(timeout=10),
                9,
            )

    def test_concurrent_cancellations_restore_reserved_stock_only_once(self):
        now = timezone.now()
        order = Order.objects.create(
            order_number="LOCK-CANCEL-001",
            user=self.user,
            status=Order.Status.PENDING_PAYMENT,
            payment_status=Order.PaymentStatus.UNPAID,
            shipping_weight_grams=100,
            subtotal_toman=100_000,
            shipping_amount_toman=0,
            total_toman=100_000,
            terms_accepted_at=now,
            stock_reserved_at=now,
            expires_at=now + timedelta(minutes=20),
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_id_snapshot=self.product.pk,
            product_name=self.product.name,
            product_slug=self.product.slug,
            product_sku=self.product.sku,
            product_unit=self.product.unit,
            unit_price_toman=100_000,
            quantity=1,
            total_price_toman=100_000,
        )
        barrier = Barrier(2)

        def cancel():
            try:
                with transaction.atomic():
                    with connections["default"].cursor() as cursor:
                        cursor.execute("SET LOCAL lock_timeout = '5s'")
                    barrier.wait(timeout=10)
                    try:
                        cancel_unpaid_order(order=order)
                    except InvalidOrderTransitionError:
                        return "already_cancelled"
                    return "cancelled"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(cancel) for _ in range(2)]
            outcomes = [future.result(timeout=15) for future in futures]

        self.assertCountEqual(outcomes, ["cancelled", "already_cancelled"])
        self.product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertIsNotNone(order.stock_released_at)
