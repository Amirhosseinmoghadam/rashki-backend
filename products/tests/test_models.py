from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from products.models import Product, ProductRelation
from .base import ProductFixture

class ProductModelTests(ProductFixture):
    def test_name_trimmed_on_save(self):
        self.assertEqual(self.product.name, "لنت ترمز تست")

    def test_slug_generated(self):
        self.assertTrue(self.product.slug)

    def test_slug_stable_after_rename(self):
        old = self.product.slug
        self.product.name = "نام متفاوت"
        self.product.save()
        self.assertEqual(self.product.slug, old)

    def test_duplicate_name_generates_distinct_slugs(self):
        duplicate = self.make_product(name=self.product.name)
        self.assertNotEqual(duplicate.slug, self.product.slug)

    def test_empty_sku_and_barcode_become_null(self):
        self.product.sku = ""
        self.product.barcode = ""
        self.product.save()
        self.assertIsNone(self.product.sku)
        self.assertIsNone(self.product.barcode)

    def test_sku_and_barcode_trimmed(self):
        self.product.sku = "  SKU-X  "
        self.product.barcode = "  12345  "
        self.product.save()
        self.assertEqual(self.product.sku, "SKU-X")
        self.assertEqual(self.product.barcode, "12345")

    def test_fixed_price_requires_base_toman(self):
        self.product.base_price_toman = None
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_usd_price_requires_base_usd(self):
        self.product.pricing_mode = Product.PricingMode.USD_BASED
        self.product.base_price_usd = None
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_active_requires_current_price(self):
        self.product.current_price_toman = None
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_draft_allows_missing_final_price(self):
        self.product.status = Product.Status.DRAFT
        self.product.current_price_toman = None
        self.product.full_clean()

    def test_negative_stock_rejected_by_validation(self):
        self.product.stock_quantity = -1
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_duplicate_sku_rejected_by_database(self):
        self.product.sku = "sku-unique-1"
        self.product.save()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_product("دیگری", sku="sku-unique-1")

    def test_relation_cannot_reference_same_product(self):
        relation = ProductRelation(product=self.product, related_product=self.product)
        with self.assertRaises(ValidationError):
            relation.full_clean()

    def test_product_string(self):
        self.assertEqual(str(self.product), self.product.name)
