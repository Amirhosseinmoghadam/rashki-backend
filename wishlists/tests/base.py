from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from categories.models import Category
from brands.models import Brand
from products.models import Product
from wishlists.models import WishlistItem

class WishlistBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(phone_number="09120000001")
        cls.other = U.objects.create_user(phone_number="09120000002")
        cls.category = Category.objects.create(name="Wishlist category", is_active=True)
        cls.brand = Brand.objects.create(name="Wishlist Brand", is_active=True)
        cls.product = cls.make_product("First wishlist product", "WL-001")
        cls.product2 = cls.make_product("Second wishlist product", "WL-002")
    @classmethod
    def make_product(cls, name, sku, **changes):
        values = dict(name=name, sku=sku, category=cls.category, brand=cls.brand,
                      pricing_mode=Product.PricingMode.FIXED, base_price_toman=100000,
                      current_price_toman=100000, status=Product.Status.ACTIVE,
                      stock_quantity=5)
        values.update(changes)
        return Product.objects.create(**values)
    def authenticated(self, user=None):
        client=APIClient(); client.force_authenticate(user=user or self.user); return client
    @property
    def list_url(self): return "/api/v1/wishlist/"
    @property
    def ids_url(self): return "/api/v1/wishlist/product-ids/"
    def item_url(self, product=None): return f"/api/v1/wishlist/{(product or self.product).pk}/"
