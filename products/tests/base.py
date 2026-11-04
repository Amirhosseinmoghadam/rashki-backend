from django.test import TestCase
from categories.models import Category
from products.models import Product

class ProductFixture(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="قطعات تست محصولات", is_active=True)
        cls.product = Product.objects.create(
            name="  لنت ترمز تست  ", category=cls.category,
            pricing_mode=Product.PricingMode.FIXED,
            base_price_toman=150000,
            current_price_toman=150000,
            stock_quantity=5,
            status=Product.Status.ACTIVE,
        )

    @classmethod
    def make_product(cls, name="محصول دیگر", **overrides):
        values = dict(name=name, category=cls.category,
                      pricing_mode=Product.PricingMode.FIXED,
                      base_price_toman=120000,
                      current_price_toman=120000,
                      status=Product.Status.ACTIVE,
                      stock_quantity=2)
        values.update(overrides)
        return Product.objects.create(**values)
