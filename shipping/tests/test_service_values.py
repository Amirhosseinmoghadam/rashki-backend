from types import SimpleNamespace
from django.test import SimpleTestCase
from shipping.services import (
    ShippingValidationError, build_unit_values_by_cart_item_id,
    calculate_packages_weight, calculate_packages_value,
    calculate_shipping_cart, build_shipping_packages,
)
from carts.services import CartValidationError
from unittest.mock import patch


class ShippingValueTests(SimpleTestCase):
    def test_unit_prices_from_available_cart_items(self):
        result = build_unit_values_by_cart_item_id(cart_calculation={"items": [
            {"id": 5, "unit_price_toman": "125000", "is_available": True},
            {"id": 6, "unit_price_toman": 900, "is_available": False},
        ]})
        self.assertEqual(result, {5: 125000})

    def test_missing_item_id_rejected(self):
        with self.assertRaises(ShippingValidationError):
            build_unit_values_by_cart_item_id(cart_calculation={"items": [
                {"id": None, "unit_price_toman": 1000, "is_available": True}
            ]})

    def test_missing_price_rejected(self):
        with self.assertRaises(ShippingValidationError):
            build_unit_values_by_cart_item_id(cart_calculation={"items": [
                {"id": 1, "unit_price_toman": None, "is_available": True}
            ]})

    def test_zero_negative_and_nonnumeric_price_rejected(self):
        for price in (0, -1, "invalid"):
            with self.subTest(price=price), self.assertRaises(ShippingValidationError):
                build_unit_values_by_cart_item_id(cart_calculation={"items": [
                    {"id": 1, "unit_price_toman": price, "is_available": True}
                ]})

    def test_no_available_items_rejected(self):
        with self.assertRaises(ShippingValidationError):
            build_unit_values_by_cart_item_id(cart_calculation={"items": []})

    def test_package_weight_total(self):
        packages = [SimpleNamespace(weight_grams=1500), SimpleNamespace(weight_grams="250")]
        self.assertEqual(calculate_packages_weight(packages), 1750)

    def test_package_weight_invalid_rejected(self):
        for value in (0, -20, "invalid", None):
            with self.subTest(value=value), self.assertRaises(ShippingValidationError):
                calculate_packages_weight([SimpleNamespace(weight_grams=value)])

    def test_empty_packages_weight_rejected(self):
        with self.assertRaises(ShippingValidationError):
            calculate_packages_weight([])

    def test_package_declared_value_total(self):
        packages = [SimpleNamespace(declared_value_toman=80000), SimpleNamespace(declared_value_toman="40000")]
        self.assertEqual(calculate_packages_value(packages), 120000)

    def test_invalid_package_declared_value_rejected(self):
        for value in (None, 0, -1, "invalid"):
            with self.subTest(value=value), self.assertRaises(ShippingValidationError):
                calculate_packages_value([SimpleNamespace(declared_value_toman=value)])

    @patch("shipping.services.calculate_cart")
    def test_cart_must_be_checkout_ready(self, calculate):
        calculate.return_value = {"is_checkout_ready": False}
        with self.assertRaises(ShippingValidationError):
            calculate_shipping_cart(cart=object())
        calculate.assert_called_once_with(calculate.call_args.args[0], strict=True)

    @patch("shipping.services.calculate_cart")
    def test_cart_error_is_normalized(self, calculate):
        calculate.side_effect = CartValidationError("invalid cart")
        with self.assertRaises(ShippingValidationError):
            calculate_shipping_cart(cart=object())

    @patch("shipping.services.build_cart_packages")
    def test_empty_packaging_rejected(self, build):
        build.return_value = []
        with self.assertRaises(ShippingValidationError):
            build_shipping_packages(cart=object(), cart_calculation={"items": [
                {"id": 1, "unit_price_toman": 1000, "is_available": True}
            ]})

    @patch("shipping.services.build_cart_packages")
    def test_packaging_receives_cart_unit_prices(self, build):
        packages = [SimpleNamespace(weight_grams=100, declared_value_toman=1000)]
        build.return_value = packages
        cart = object()
        self.assertIs(build_shipping_packages(cart=cart, cart_calculation={"items": [
            {"id": 3, "unit_price_toman": 1000, "is_available": True}
        ]}), packages)
        build.assert_called_once_with(cart=cart, unit_values_by_cart_item_id={3: 1000})
