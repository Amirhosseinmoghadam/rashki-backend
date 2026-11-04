from types import SimpleNamespace
from unittest.mock import patch
from django.test import TestCase
from orders.services import (
    OrderValidationError, create_order_from_cart,
    calculate_locked_package_weight, validate_locked_product,
)
from products.models import Product


class CheckoutValidationTests(TestCase):
    def test_terms_must_be_accepted_before_database_access(self):
        with self.assertRaises(OrderValidationError):
            create_order_from_cart(user=None, address_id=1, shipping_method_id=1, accept_terms=False)

    @patch('orders.services.Cart.objects')
    def test_missing_cart_is_rejected(self, objects):
        objects.select_for_update.return_value.select_related.return_value.filter.return_value.first.return_value = None
        with self.assertRaisesMessage(OrderValidationError, 'سبد خرید خالی است'):
            create_order_from_cart(user=None, address_id=1, shipping_method_id=1, accept_terms=True)

    def test_unavailable_product_rejected(self):
        product = SimpleNamespace(name='test', status='inactive', category_id=1, brand_id=None, current_price_toman=100, stock_quantity=10)
        with self.assertRaises(OrderValidationError):
            validate_locked_product(product=product, quantity=1, public_category_ids={1})

    def test_inactive_category_rejected(self):
        product = SimpleNamespace(name='test', status=Product.Status.ACTIVE, category_id=99, brand_id=None, current_price_toman=100, stock_quantity=10)
        with self.assertRaises(OrderValidationError):
            validate_locked_product(product=product, quantity=1, public_category_ids={1})

    def test_inactive_brand_rejected(self):
        product = SimpleNamespace(name='test', status=Product.Status.ACTIVE, category_id=1, brand_id=3, brand=SimpleNamespace(is_active=False), current_price_toman=100, stock_quantity=10)
        with self.assertRaises(OrderValidationError):
            validate_locked_product(product=product, quantity=1, public_category_ids={1})

    def test_missing_price_rejected(self):
        product = SimpleNamespace(name='test', status=Product.Status.ACTIVE, category_id=1, brand_id=None, current_price_toman=None, stock_quantity=10)
        with self.assertRaises(OrderValidationError):
            validate_locked_product(product=product, quantity=1, public_category_ids={1})

    def test_insufficient_stock_rejected(self):
        product = SimpleNamespace(name='test', status=Product.Status.ACTIVE, category_id=1, brand_id=None, current_price_toman=100, stock_quantity=2)
        with self.assertRaisesMessage(OrderValidationError, 'کافی نیست'):
            validate_locked_product(product=product, quantity=3, public_category_ids={1})

    def test_valid_product_accepted(self):
        product = SimpleNamespace(name='test', status=Product.Status.ACTIVE, category_id=1, brand_id=None, current_price_toman=100, stock_quantity=3)
        self.assertIsNone(validate_locked_product(product=product, quantity=3, public_category_ids={1}))

    def test_missing_weight_rejected(self):
        item = SimpleNamespace(product=SimpleNamespace(weight_grams=None, name='test'), quantity=1)
        with self.assertRaises(OrderValidationError):
            calculate_locked_package_weight([item])

    @patch('orders.services.ShippingSettings.load')
    def test_weight_includes_packaging(self, load):
        load.return_value.package_extra_weight_grams = 100
        item = SimpleNamespace(product=SimpleNamespace(weight_grams=250), quantity=3)
        self.assertEqual(calculate_locked_package_weight([item]), 850)

    @patch('orders.services.ShippingSettings.load')
    def test_zero_weight_rejected(self, load):
        load.return_value.package_extra_weight_grams = 0
        item = SimpleNamespace(product=SimpleNamespace(weight_grams=0), quantity=1)
        with self.assertRaises(OrderValidationError):
            calculate_locked_package_weight([item])
