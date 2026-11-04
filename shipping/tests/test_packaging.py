from decimal import Decimal
from types import SimpleNamespace
from django.test import SimpleTestCase
from shipping.packaging.base import ShippingPackage, ShippingPackageItem
from shipping.packaging.selector import _decimal, _orientations, _find_fitting_orientation, PackagingSelectionError
from shipping.packaging.service import validate_product_shipping_data, CartPackagingError


class PackagingTests(SimpleTestCase):
    def test_package_volume(self):
        package = ShippingPackage(weight_grams=400, length_cm=Decimal("20"),
            width_cm=Decimal("10"), height_cm=Decimal("5"), items=())
        self.assertEqual(package.volume_cm3, Decimal("1000"))

    def test_package_metadata_independent(self):
        a = ShippingPackage(100, Decimal(1), Decimal(1), Decimal(1), ())
        b = ShippingPackage(100, Decimal(1), Decimal(1), Decimal(1), ())
        a.metadata["flag"] = 1
        self.assertEqual(b.metadata, {})

    def test_item_is_immutable(self):
        from dataclasses import FrozenInstanceError
        item = ShippingPackageItem(1, "item", 1, 100, Decimal(1), Decimal(2), Decimal(3))
        with self.assertRaises(FrozenInstanceError):
            item.quantity = 5

    def test_decimal_parsing(self):
        self.assertEqual(_decimal("2.50", field_name="length"), Decimal("2.50"))

    def test_invalid_dimensions(self):
        for value in (0, -1, "garbage", None):
            with self.subTest(value=value), self.assertRaises(PackagingSelectionError):
                _decimal(value, field_name="length")

    def test_unique_orientations(self):
        self.assertEqual(len(_orientations(2, 2, 3)), 3)
        self.assertEqual(len(_orientations(2, 3, 4)), 6)

    def test_product_rotates_to_fit(self):
        result = _find_fitting_orientation(item_length=30, item_width=10, item_height=20,
            box_length=10, box_width=20, box_height=30)
        self.assertIsNotNone(result)

    def test_product_too_large(self):
        result = _find_fitting_orientation(item_length=30, item_width=20, item_height=10,
            box_length=5, box_width=5, box_height=5)
        self.assertIsNone(result)

    def test_missing_product_weight(self):
        product = SimpleNamespace(weight_grams=None, shipping_length_cm=10,
                                  shipping_width_cm=10, shipping_height_cm=10)
        with self.assertRaises(CartPackagingError):
            validate_product_shipping_data(product)

    def test_missing_product_dimensions(self):
        product = SimpleNamespace(weight_grams=100, shipping_length_cm=None,
                                  shipping_width_cm=10, shipping_height_cm=10)
        with self.assertRaises(CartPackagingError):
            validate_product_shipping_data(product)

    def test_valid_product_shipping_data(self):
        product = SimpleNamespace(weight_grams=100, shipping_length_cm=10,
                                  shipping_width_cm=10, shipping_height_cm=10)
        self.assertIsNone(validate_product_shipping_data(product))
