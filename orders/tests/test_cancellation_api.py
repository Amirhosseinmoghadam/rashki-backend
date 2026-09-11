import uuid

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from addresses.models import (
    Address,
    City,
    Province,
)

from categories.models import (
    Category,
)

from orders.models import (
    Order,
    OrderItem,
)

from orders.services import (
    mark_order_paid,
)

from payments.models import (
    PaymentAttempt,
    PaymentRefund,
)

from payments.providers.base import (
    PaymentProviderIndeterminateError,
)

from products.models import (
    Product,
)

from shipping.models import (
    Shipment,
    ShippingMethod,
)

from shipping.providers.tipax_client import (
    TipaxIndeterminateError,
)


# =========================================================
# Fake Payment Providers
# =========================================================


class FakeSuccessfulPaymentProvider:
    """
    Reversal موفق زرین‌پال.
    """

    def __init__(self):
        self.reverse_calls = 0

    def reverse_payment(
        self,
        *,
        attempt,
    ):
        self.reverse_calls += 1

        return {
            "success": True,
            "code": 100,
            "message": "Mock Reversed",
            "test_mode": True,
        }


class FakeIndeterminatePaymentProvider:
    """
    Request به Provider ارسال شده،
    ولی نتیجه آن نامشخص است.
    """

    def __init__(self):
        self.reverse_calls = 0

    def reverse_payment(
        self,
        *,
        attempt,
    ):
        self.reverse_calls += 1

        raise PaymentProviderIndeterminateError(
            (
                "Mock ZarinPal reversal timeout: "
                "provider result unknown"
            )
        )


# =========================================================
# Cancellation API Tests
# =========================================================


class OrderCancellationAPITests(
    APITestCase
):

    # =====================================================
    # Setup
    # =====================================================

    def setUp(self):
        super().setUp()

        # -------------------------------------------------
        # User
        # -------------------------------------------------

        self.user = self._create_test_user(
            phone_number="09120000001",
            first_name="کاربر",
            last_name="تست",
        )

        # -------------------------------------------------
        # Province
        # -------------------------------------------------
        #
        # این داده داخلی است.
        #
        # اگر بعداً Province/City از Tipax Sync شوند،
        # تغییرات مربوط به Provider فقط در Setup تست
        # اعمال می‌شود.
        # -------------------------------------------------

        self.province = (
            Province.objects.create(
                name="استان تست"
            )
        )

        # -------------------------------------------------
        # City
        # -------------------------------------------------

        self.city = (
            City.objects.create(
                province=self.province,
                name="شهر تست",
            )
        )

        # -------------------------------------------------
        # Address
        # -------------------------------------------------

        self.address = (
            Address.objects.create(
                user=self.user,

                first_name="کاربر",
                last_name="تست",

                mobile_number=(
                    "09120000001"
                ),

                phone_number=(
                    "02112345678"
                ),

                province=self.province,
                city=self.city,

                postal_code=(
                    "1234567890"
                ),

                postal_address=(
                    "آدرس تست برای "
                    "Cancellation API"
                ),

                is_default=True,
            )
        )

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        self.category = (
            Category.objects.create(
                name=(
                    "دسته تست لغو سفارش"
                ),

                slug=(
                    "cancellation-test-category"
                ),

                description="",

                is_active=True,
            )
        )

        # -------------------------------------------------
        # Product
        # -------------------------------------------------

        self.initial_stock = 10

        self.product = (
            Product.objects.create(
                name=(
                    "محصول تست لغو سفارش"
                ),

                slug=(
                    "cancellation-test-product"
                ),

                category=self.category,

                sku=(
                    "CANCEL-TEST-001"
                ),

                current_price_toman=(
                    681_000
                ),

                stock_quantity=(
                    self.initial_stock
                ),

                weight_grams=850,

                status=(
                    Product.Status.ACTIVE
                ),
            )
        )

        # -------------------------------------------------
        # Shipping Method
        # -------------------------------------------------

        self.shipping_method = (
            ShippingMethod.objects.create(
                code=(
                    "tipax-cancellation-test"
                ),

                name=(
                    "Tipax Test"
                ),

                provider="tipax",

                service_code="1",

                calculation_mode=(
                    ShippingMethod
                    .CalculationMode
                    .MANUAL
                ),

                description=(
                    "Cancellation test method"
                ),

                is_active=True,

                sort_order=0,
            )
        )

        # -------------------------------------------------
        # Authentication
        # -------------------------------------------------

        self.client.force_authenticate(
            user=self.user
        )

    # =====================================================
    # User Factory
    # =====================================================

    def _create_test_user(
        self,
        *,
        phone_number,
        first_name,
        last_name,
    ):
        """
        اگر accounts در آینده تغییر کند،
        فقط این Helper نیاز به اصلاح دارد.
        """

        User = get_user_model()

        user = User.objects.create(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_phone_verified=True,
        )

        user.set_password(
            "TestPassword123!"
        )

        user.save(
            update_fields=[
                "password",
            ]
        )

        return user

    # =====================================================
    # Order Number
    # =====================================================

    def _generate_order_number(self):
        return (
            "RK-TEST-"
            + uuid.uuid4()
            .hex[:8]
            .upper()
        )

    # =====================================================
    # Create Reserved Order
    # =====================================================

    def _create_reserved_order(
        self,
        *,
        customer_note="Cancellation Test",
    ):
        """
        یک Order در وضعیت واقعی قبل از Payment می‌سازد.

        نکته مهم:

        این تست قرار نیست Checkout یا Packaging
        را آزمایش کند.

        بنابراین:

            create_order_from_cart()

        عمداً استفاده نمی‌شود.

        در عوض Precondition موردنیاز Cancellation
        را مستقیم می‌سازیم:

            Order
            OrderItem
            Reserved Stock

        این باعث می‌شود تست Cancellation از:

            Tipax Carton
            Packaging Rules
            Shipping Quote
            City Mapping
            Provider API

        مستقل باشد.
        """

        now = timezone.now()

        # -------------------------------------------------
        # Order
        # -------------------------------------------------

        order = Order.objects.create(

            order_number=(
                self._generate_order_number()
            ),

            user=self.user,

            status=(
                Order.Status.PENDING_PAYMENT
            ),

            payment_status=(
                Order.PaymentStatus.UNPAID
            ),

            # ---------------------------------------------
            # Address
            # ---------------------------------------------

            address=self.address,

            shipping_first_name=(
                self.address.first_name
                or ""
            ),

            shipping_last_name=(
                self.address.last_name
                or ""
            ),

            shipping_mobile_number=(
                self.address.mobile_number
                or ""
            ),

            shipping_phone_number=(
                self.address.phone_number
                or ""
            ),

            shipping_province_name=(
                self.province.name
            ),

            shipping_city_name=(
                self.city.name
            ),

            shipping_postal_code=(
                self.address.postal_code
                or ""
            ),

            shipping_postal_address=(
                self.address.postal_address
                or ""
            ),

            # ---------------------------------------------
            # Shipping
            # ---------------------------------------------

            shipping_method=(
                self.shipping_method
            ),

            shipping_method_code=(
                self.shipping_method.code
            ),

            shipping_method_name=(
                self.shipping_method.name
            ),

            shipping_provider=(
                self.shipping_method.provider
            ),

            shipping_service_code=(
                self.shipping_method.service_code
            ),

            shipping_weight_grams=850,

            shipping_provider_data={
                "test_mode": True,
            },

            # ---------------------------------------------
            # Money
            # ---------------------------------------------

            subtotal_toman=681_000,

            eligible_discount_subtotal_toman=0,

            discount_amount_toman=0,

            shipping_amount_toman=10_000,

            total_toman=691_000,

            # ---------------------------------------------
            # Metadata
            # ---------------------------------------------

            customer_note=(
                customer_note
            ),

            terms_accepted_at=now,

            stock_reserved_at=now,

            stock_released_at=None,

            expires_at=(
                now
                + timedelta(
                    minutes=20
                )
            ),
        )

        # -------------------------------------------------
        # OrderItem Snapshot
        # -------------------------------------------------

        OrderItem.objects.create(

            order=order,

            product=self.product,

            product_id_snapshot=(
                self.product.id
            ),

            product_name=(
                self.product.name
            ),

            product_slug=(
                self.product.slug
            ),

            product_sku=(
                self.product.sku
                or ""
            ),

            product_brand_name="",

            product_unit=(
                self.product.unit
            ),

            unit_price_toman=(
                self.product
                .current_price_toman
            ),

            quantity=1,

            total_price_toman=(
                self.product
                .current_price_toman
            ),
        )

        # -------------------------------------------------
        # Reserve Stock
        # -------------------------------------------------

        self.product.refresh_from_db()

        self.product.stock_quantity -= 1

        self.product.save(
            update_fields=[
                "stock_quantity",
            ]
        )

        # -------------------------------------------------
        # Verify Precondition
        # -------------------------------------------------

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock_quantity,
            self.initial_stock - 1,
        )

        return order

    # =====================================================
    # Make Order Paid
    # =====================================================

    def _make_order_paid(
        self,
        order,
    ):
        """
        Payment Provider واقعی اجرا نمی‌شود.

        PaymentAttempt موفقی مشابه نتیجه Verify
        ساخته می‌شود و سپس Order با Service واقعی
        به PAID منتقل می‌شود.
        """

        now = timezone.now()

        attempt = (
            PaymentAttempt.objects.create(

                order=order,

                provider=(
                    PaymentAttempt
                    .Provider
                    .ZARINPAL
                ),

                status=(
                    PaymentAttempt
                    .Status
                    .SUCCEEDED
                ),

                amount_toman=(
                    order.total_toman
                ),

                provider_amount=(
                    order.total_toman
                ),

                provider_currency="IRT",

                provider_adjustment_toman=0,

                provider_reference=(
                    f"MOCK-AUTH-"
                    f"{order.id}"
                ),

                provider_transaction_id=(
                    f"MOCK-REF-"
                    f"{order.id}"
                ),

                provider_session_id="",

                gateway_url="",

                idempotency_key=(
                    f"test-payment-"
                    f"{order.id}"
                ),

                request_payload={
                    "test_mode": True,
                },

                response_payload={
                    "code": 100,
                    "test_mode": True,
                },

                callback_payload={
                    "Status": "OK",
                },

                failure_code="",

                failure_message="",

                started_at=now,

                expires_at=(
                    order.expires_at
                ),

                verified_at=now,
            )
        )

        order = mark_order_paid(
            order
        )

        return (
            order,
            attempt,
        )

    # =====================================================
    # Shipment Factory
    # =====================================================

    def _create_registered_shipment(
        self,
        order,
    ):
        return (
            Shipment.objects.create(

                order=order,

                shipping_method=(
                    self.shipping_method
                ),

                provider="tipax",

                status=(
                    Shipment
                    .Status
                    .REGISTERED
                ),

                external_order_id=(
                    f"MOCK-TIPAX-"
                    f"{order.id}"
                ),

                tracking_codes=[
                    (
                        f"MOCK-TRACK-"
                        f"{order.id}"
                    )
                ],

                primary_tracking_code=(
                    f"MOCK-TRACK-"
                    f"{order.id}"
                ),

                quoted_amount_toman=(
                    order
                    .shipping_amount_toman
                ),

                request_payload={
                    "test_mode": True,
                },

                response_payload={
                    "test_mode": True,

                    "orderId": (
                        f"MOCK-TIPAX-"
                        f"{order.id}"
                    ),
                },
            )
        )

    # =====================================================
    # Cancel URL
    # =====================================================

    def _cancel_url(
        self,
        order,
    ):
        return reverse(
            (
                "orders_api_v1:"
                "order-cancel"
            ),

            kwargs={
                "order_number": (
                    order.order_number
                ),
            },
        )

    # =====================================================
    # Cancel API
    # =====================================================

    def _cancel_order(
        self,
        order,
        *,
        description="Cancellation Test",
    ):
        return self.client.post(

            self._cancel_url(
                order
            ),

            {
                "reason": (
                    "customer_request"
                ),

                "description": (
                    description
                ),
            },

            format="json",
        )

    # =====================================================
    # Test 1
    #
    # Unpaid Cancellation
    # =====================================================

    def test_unpaid_order_can_be_cancelled_and_stock_is_restored(
        self,
    ):
        order = (
            self._create_reserved_order(
                customer_note=(
                    "Unpaid Cancellation Test"
                )
            )
        )

        # -------------------------------------------------
        # Before
        # -------------------------------------------------

        self.assertEqual(
            order.status,
            Order.Status.PENDING_PAYMENT,
        )

        self.assertEqual(
            order.payment_status,
            Order.PaymentStatus.UNPAID,
        )

        self.assertIsNone(
            order.stock_released_at
        )

        # -------------------------------------------------
        # Cancel
        # -------------------------------------------------

        response = (
            self._cancel_order(
                order
            )
        )

        # -------------------------------------------------
        # Refresh
        # -------------------------------------------------

        order.refresh_from_db()

        self.product.refresh_from_db()

        # -------------------------------------------------
        # API
        # -------------------------------------------------

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data[
                "success"
            ]
        )

        self.assertFalse(
            response.data[
                "data"
            ][
                "already_cancelled"
            ]
        )

        # -------------------------------------------------
        # Order
        # -------------------------------------------------

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED,
        )

        self.assertEqual(
            order.payment_status,
            Order.PaymentStatus.UNPAID,
        )

        self.assertIsNotNone(
            order.cancelled_at
        )

        self.assertIsNotNone(
            order.stock_released_at
        )

        # -------------------------------------------------
        # Stock
        # -------------------------------------------------

        self.assertEqual(
            self.product.stock_quantity,
            self.initial_stock,
        )

        # -------------------------------------------------
        # Refund
        # -------------------------------------------------

        self.assertFalse(
            PaymentRefund.objects.filter(
                order=order
            ).exists()
        )

    # =====================================================
    # Test 2
    #
    # Paid + Tipax Success + Refund Success
    # =====================================================

    def test_paid_order_cancellation_cancels_tipax_refunds_and_restores_stock(
        self,
    ):
        order = (
            self._create_reserved_order(
                customer_note=(
                    "Paid Cancellation Test"
                )
            )
        )

        (
            order,
            attempt,
        ) = (
            self._make_order_paid(
                order
            )
        )

        shipment = (
            self._create_registered_shipment(
                order
            )
        )

        payment_provider = (
            FakeSuccessfulPaymentProvider()
        )

        # -------------------------------------------------
        # External Mocks
        # -------------------------------------------------

        with (
            patch(
                (
                    "shipping.shipments.tipax."
                    "TipaxClient.cancel_order"
                ),

                return_value={
                    "isSuccess": True,

                    "message": (
                        "Mock Tipax Cancelled"
                    ),
                },
            ) as tipax_cancel_mock,

            patch(
                (
                    "payments.services."
                    "get_payment_provider"
                ),

                return_value=(
                    payment_provider
                ),
            ) as payment_provider_mock,
        ):

            # ---------------------------------------------
            # First Request
            # ---------------------------------------------

            response = (
                self._cancel_order(
                    order
                )
            )

            order.refresh_from_db()

            shipment.refresh_from_db()

            self.product.refresh_from_db()

            refund = (
                PaymentRefund.objects.get(
                    order=order
                )
            )

            # ---------------------------------------------
            # API
            # ---------------------------------------------

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
            )

            # ---------------------------------------------
            # Shipment
            # ---------------------------------------------

            self.assertEqual(
                shipment.status,
                Shipment.Status.CANCELLED,
            )

            self.assertIsNotNone(
                shipment.cancelled_at
            )

            self.assertEqual(
                (
                    shipment
                    .tracking_payload[
                        "cancellation"
                    ][
                        "result"
                    ]
                ),
                "succeeded",
            )

            # ---------------------------------------------
            # Refund
            # ---------------------------------------------

            self.assertEqual(
                refund.status,
                PaymentRefund.Status.SUCCEEDED,
            )

            self.assertEqual(
                refund.amount_toman,
                attempt.amount_toman,
            )

            # ---------------------------------------------
            # Order
            # ---------------------------------------------

            self.assertEqual(
                order.status,
                Order.Status.CANCELLED,
            )

            self.assertEqual(
                order.payment_status,
                Order.PaymentStatus.REFUNDED,
            )

            self.assertIsNotNone(
                order.stock_released_at
            )

            # ---------------------------------------------
            # Stock
            # ---------------------------------------------

            self.assertEqual(
                self.product.stock_quantity,
                self.initial_stock,
            )

            # ---------------------------------------------
            # External Calls
            # ---------------------------------------------

            self.assertEqual(
                tipax_cancel_mock.call_count,
                1,
            )

            self.assertEqual(
                payment_provider_mock.call_count,
                1,
            )

            self.assertEqual(
                payment_provider.reverse_calls,
                1,
            )

            # =============================================
            # Idempotency
            # =============================================

            second_response = (
                self._cancel_order(
                    order,
                    description=(
                        "Second cancellation"
                    ),
                )
            )

            order.refresh_from_db()

            self.product.refresh_from_db()

            self.assertEqual(
                second_response.status_code,
                status.HTTP_200_OK,
            )

            self.assertTrue(
                second_response.data[
                    "data"
                ][
                    "already_cancelled"
                ]
            )

            # Tipax دوباره اجرا نمی‌شود.
            self.assertEqual(
                tipax_cancel_mock.call_count,
                1,
            )

            # Reversal دوباره اجرا نمی‌شود.
            self.assertEqual(
                payment_provider.reverse_calls,
                1,
            )

            # Refund تکراری ساخته نمی‌شود.
            self.assertEqual(
                PaymentRefund.objects.filter(
                    order=order
                ).count(),
                1,
            )

            # Double Restock رخ نمی‌دهد.
            self.assertEqual(
                self.product.stock_quantity,
                self.initial_stock,
            )

    # =====================================================
    # Test 3
    #
    # Tipax Indeterminate
    # =====================================================

    def test_tipax_indeterminate_stops_before_refund_and_requires_review(
        self,
    ):
        order = (
            self._create_reserved_order(
                customer_note=(
                    "Tipax Indeterminate Test"
                )
            )
        )

        order, _ = (
            self._make_order_paid(
                order
            )
        )

        shipment = (
            self._create_registered_shipment(
                order
            )
        )

        # -------------------------------------------------
        # Unknown Tipax Result
        # -------------------------------------------------

        with (
            patch(
                (
                    "shipping.shipments.tipax."
                    "TipaxClient.cancel_order"
                ),

                side_effect=(
                    TipaxIndeterminateError(
                        "Mock Tipax timeout"
                    )
                ),
            ) as tipax_cancel_mock,

            patch(
                (
                    "payments.services."
                    "get_payment_provider"
                ),
            ) as payment_provider_mock,
        ):

            response = (
                self._cancel_order(
                    order
                )
            )

        # -------------------------------------------------
        # Refresh
        # -------------------------------------------------

        order.refresh_from_db()

        shipment.refresh_from_db()

        self.product.refresh_from_db()

        # -------------------------------------------------
        # HTTP 409
        # -------------------------------------------------

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertFalse(
            response.data[
                "success"
            ]
        )

        self.assertTrue(
            response.data[
                "errors"
            ][
                "review_required"
            ]
        )

        # -------------------------------------------------
        # Order unchanged
        # -------------------------------------------------

        self.assertEqual(
            order.status,
            Order.Status.PROCESSING,
        )

        self.assertEqual(
            order.payment_status,
            Order.PaymentStatus.PAID,
        )

        # -------------------------------------------------
        # Shipment remains Registered
        # -------------------------------------------------

        self.assertEqual(
            shipment.status,
            Shipment.Status.REGISTERED,
        )

        self.assertIsNone(
            shipment.cancelled_at
        )

        # -------------------------------------------------
        # Audit
        # -------------------------------------------------

        cancellation_data = (
            shipment
            .tracking_payload
            .get(
                "cancellation",
                {}
            )
        )

        self.assertEqual(
            cancellation_data.get(
                "result"
            ),
            "indeterminate",
        )

        # -------------------------------------------------
        # No Refund
        # -------------------------------------------------

        self.assertFalse(
            PaymentRefund.objects.filter(
                order=order
            ).exists()
        )

        # -------------------------------------------------
        # Payment Provider NOT reached
        # -------------------------------------------------

        self.assertEqual(
            payment_provider_mock.call_count,
            0,
        )

        # -------------------------------------------------
        # Stock remains reserved
        # -------------------------------------------------

        self.assertEqual(
            self.product.stock_quantity,
            self.initial_stock - 1,
        )

        self.assertIsNone(
            order.stock_released_at
        )

        self.assertEqual(
            tipax_cancel_mock.call_count,
            1,
        )

    # =====================================================
    # Test 4
    #
    # ZarinPal Indeterminate + Retry Safety
    # =====================================================

    def test_zarinpal_indeterminate_requires_review_and_does_not_retry(
        self,
    ):
        order = (
            self._create_reserved_order(
                customer_note=(
                    "ZarinPal Indeterminate Test"
                )
            )
        )

        (
            order,
            attempt,
        ) = (
            self._make_order_paid(
                order
            )
        )

        shipment = (
            self._create_registered_shipment(
                order
            )
        )

        payment_provider = (
            FakeIndeterminatePaymentProvider()
        )

        # -------------------------------------------------
        # External Mocks
        # -------------------------------------------------

        with (
            patch(
                (
                    "shipping.shipments.tipax."
                    "TipaxClient.cancel_order"
                ),

                return_value={
                    "isSuccess": True,

                    "message": (
                        "Mock Tipax Cancelled"
                    ),
                },
            ) as tipax_cancel_mock,

            patch(
                (
                    "payments.services."
                    "get_payment_provider"
                ),

                return_value=(
                    payment_provider
                ),
            ) as payment_provider_mock,
        ):

            # =============================================
            # First Request
            # =============================================

            first_response = (
                self._cancel_order(
                    order
                )
            )

            order.refresh_from_db()

            shipment.refresh_from_db()

            self.product.refresh_from_db()

            refund = (
                PaymentRefund.objects.get(
                    order=order
                )
            )

            # ---------------------------------------------
            # API
            # ---------------------------------------------

            self.assertEqual(
                first_response.status_code,
                status.HTTP_409_CONFLICT,
            )

            self.assertTrue(
                first_response.data[
                    "errors"
                ][
                    "review_required"
                ]
            )

            # ---------------------------------------------
            # Shipment cancelled
            # ---------------------------------------------

            self.assertEqual(
                shipment.status,
                Shipment.Status.CANCELLED,
            )

            self.assertIsNotNone(
                shipment.cancelled_at
            )

            self.assertEqual(
                (
                    shipment
                    .tracking_payload[
                        "cancellation"
                    ][
                        "result"
                    ]
                ),
                "succeeded",
            )

            # ---------------------------------------------
            # Refund review
            # ---------------------------------------------

            self.assertEqual(
                refund.status,
                (
                    PaymentRefund
                    .Status
                    .REQUIRES_REVIEW
                ),
            )

            self.assertEqual(
                refund.failure_code,
                "provider_result_unknown",
            )

            self.assertEqual(
                refund.amount_toman,
                attempt.amount_toman,
            )

            # ---------------------------------------------
            # Order remains Paid
            # ---------------------------------------------

            self.assertEqual(
                order.status,
                Order.Status.PROCESSING,
            )

            self.assertEqual(
                order.payment_status,
                Order.PaymentStatus.PAID,
            )

            # ---------------------------------------------
            # Stock remains reserved
            # ---------------------------------------------

            self.assertEqual(
                self.product.stock_quantity,
                self.initial_stock - 1,
            )

            self.assertIsNone(
                order.stock_released_at
            )

            # ---------------------------------------------
            # External calls
            # ---------------------------------------------

            self.assertEqual(
                tipax_cancel_mock.call_count,
                1,
            )

            self.assertEqual(
                payment_provider_mock.call_count,
                1,
            )

            self.assertEqual(
                payment_provider.reverse_calls,
                1,
            )

            # =============================================
            # Second Request
            #
            # Automatic Retry must NOT happen
            # =============================================

            second_response = (
                self._cancel_order(
                    order,
                    description=(
                        "Automatic retry safety test"
                    ),
                )
            )

            order.refresh_from_db()

            shipment.refresh_from_db()

            self.product.refresh_from_db()

            refund.refresh_from_db()

            # ---------------------------------------------
            # Still 409
            # ---------------------------------------------

            self.assertEqual(
                second_response.status_code,
                status.HTTP_409_CONFLICT,
            )

            self.assertTrue(
                second_response.data[
                    "errors"
                ][
                    "review_required"
                ]
            )

            # ---------------------------------------------
            # Tipax NOT retried
            # ---------------------------------------------

            self.assertEqual(
                tipax_cancel_mock.call_count,
                1,
            )

            # ---------------------------------------------
            # Reversal NOT retried
            # ---------------------------------------------

            self.assertEqual(
                payment_provider.reverse_calls,
                1,
            )

            self.assertEqual(
                payment_provider_mock.call_count,
                1,
            )

            # ---------------------------------------------
            # One Refund only
            # ---------------------------------------------

            self.assertEqual(
                PaymentRefund.objects.filter(
                    order=order
                ).count(),
                1,
            )

            self.assertEqual(
                refund.status,
                (
                    PaymentRefund
                    .Status
                    .REQUIRES_REVIEW
                ),
            )

            # ---------------------------------------------
            # Order / Stock remain unchanged
            # ---------------------------------------------

            self.assertEqual(
                order.status,
                Order.Status.PROCESSING,
            )

            self.assertEqual(
                order.payment_status,
                Order.PaymentStatus.PAID,
            )

            self.assertEqual(
                self.product.stock_quantity,
                self.initial_stock - 1,
            )

            self.assertIsNone(
                order.stock_released_at
            )

    # =====================================================
    # Test 5
    #
    # Ownership
    # =====================================================

    def test_customer_cannot_cancel_another_users_order(
        self,
    ):
        order = (
            self._create_reserved_order(
                customer_note=(
                    "Ownership Test"
                )
            )
        )

        # -------------------------------------------------
        # Other User
        # -------------------------------------------------

        other_user = (
            self._create_test_user(
                phone_number=(
                    "09120000002"
                ),

                first_name=(
                    "کاربر"
                ),

                last_name=(
                    "دیگر"
                ),
            )
        )

        self.client.force_authenticate(
            user=other_user
        )

        # -------------------------------------------------
        # Unauthorized Cancel
        # -------------------------------------------------

        response = (
            self._cancel_order(
                order
            )
        )

        # -------------------------------------------------
        # Refresh
        # -------------------------------------------------

        order.refresh_from_db()

        self.product.refresh_from_db()

        # -------------------------------------------------
        # Hide Order Existence
        # -------------------------------------------------

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            response.data[
                "success"
            ]
        )

        # -------------------------------------------------
        # Order unchanged
        # -------------------------------------------------

        self.assertEqual(
            order.status,
            Order.Status.PENDING_PAYMENT,
        )

        self.assertEqual(
            order.payment_status,
            Order.PaymentStatus.UNPAID,
        )

        self.assertIsNone(
            order.cancelled_at
        )

        self.assertIsNone(
            order.stock_released_at
        )

        # -------------------------------------------------
        # Stock remains reserved
        # -------------------------------------------------

        self.assertEqual(
            self.product.stock_quantity,
            self.initial_stock - 1,
        )

        # -------------------------------------------------
        # No Refund
        # -------------------------------------------------

        self.assertFalse(
            PaymentRefund.objects.filter(
                order=order
            ).exists()
        )