from wishlists.models import WishlistItem
from wishlists.api.v1.serializers import WishlistItemSerializer, WishlistProductSerializer
from .base import WishlistBase

class WishlistSerializerTests(WishlistBase):
    def test_item_output_fields(self):
        item=WishlistItem.objects.create(user=self.user,product=self.product)
        data=WishlistItemSerializer(item).data
        self.assertEqual(set(data),{"id","product","created_at"})
    def test_item_product_is_nested(self):
        item=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertEqual(WishlistItemSerializer(item).data["product"]["id"],self.product.pk)
    def test_category_is_nested(self):
        data=WishlistProductSerializer(self.product).data
        self.assertEqual(data["category"]["id"],self.category.pk)
    def test_brand_is_nested(self):
        data=WishlistProductSerializer(self.product).data
        self.assertEqual(data["brand"]["id"],self.brand.pk)
    def test_no_primary_image_returns_null(self):
        self.assertIsNone(WishlistProductSerializer(self.product).data["primary_image"])
    def test_product_in_stock(self):
        self.assertTrue(WishlistProductSerializer(self.product).data["is_in_stock"])
    def test_out_of_stock(self):
        self.product.stock_quantity=0
        self.assertFalse(WishlistProductSerializer(self.product).data["is_in_stock"])
    def test_price_is_returned(self):
        self.assertEqual(WishlistProductSerializer(self.product).data["current_price_toman"],100000)
    def test_item_serializer_is_read_only(self):
        serializer=WishlistItemSerializer(data={"product":self.product.pk})
        self.assertTrue(serializer.is_valid(),serializer.errors)
        self.assertEqual(serializer.validated_data,{})
