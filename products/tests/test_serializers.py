from products.api.v1.serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    is_category_tree_active, get_category_tree_ids,
)
from categories.models import Category
from .base import ProductFixture

class ProductSerializerTests(ProductFixture):
    def test_list_exposes_name_and_price(self):
        result = ProductListSerializer(self.product).data
        self.assertEqual(result["name"], self.product.name)
        self.assertEqual(int(result["current_price_toman"]), 150000)

    def test_detail_has_stock_flag(self):
        result = ProductDetailSerializer(self.product).data
        self.assertTrue(result["is_in_stock"])

    def test_zero_stock_is_out_of_stock(self):
        self.product.stock_quantity = 0
        result = ProductDetailSerializer(self.product).data
        self.assertFalse(result["is_in_stock"])

    def test_slug_is_read_only_on_write(self):
        serializer = ProductCreateUpdateSerializer()
        self.assertTrue(serializer.fields["slug"].read_only)

    def test_calculated_price_is_read_only(self):
        serializer = ProductCreateUpdateSerializer()
        self.assertTrue(serializer.fields["current_price_toman"].read_only)

    def test_blank_name_rejected(self):
        serializer = ProductCreateUpdateSerializer(instance=self.product, data={"name":"  "}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_negative_stock_rejected(self):
        serializer = ProductCreateUpdateSerializer(instance=self.product, data={"stock_quantity": -1}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_fixed_mode_without_price_rejected(self):
        serializer = ProductCreateUpdateSerializer(data={"name":"کالای جدید", "category": self.category.pk,
                                                       "pricing_mode":"fixed", "status":"draft"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("base_price_toman", serializer.errors)

    def test_category_tree_includes_ancestors(self):
        child = Category.objects.create(name="زیر دسته تست", parent=self.category, is_active=True)
        self.assertEqual(get_category_tree_ids(child), [child.pk, self.category.pk])

    def test_inactive_parent_disables_child(self):
        child = Category.objects.create(name="زیر دسته تست", parent=self.category, is_active=True)
        self.category.is_active = False
        self.category.save()
        self.assertFalse(is_category_tree_active(child))

    def test_active_tree_accepted(self):
        self.assertTrue(is_category_tree_active(self.category))
