from django.core.exceptions import ValidationError
from products.models import ProductImage
from .base import ProductFixture

class ProductImageContractTests(ProductFixture):
    def test_limit_is_twenty(self):
        self.assertEqual(ProductImage.MAX_IMAGES_PER_PRODUCT, 20)

    def test_primary_defaults_false(self):
        image = ProductImage(product=self.product, image="products/test.jpg")
        self.assertFalse(image.is_primary)

    def test_image_belongs_to_product(self):
        image = ProductImage.objects.create(product=self.product, image="products/test.jpg")
        self.assertEqual(image.product_id, self.product.pk)

    def test_first_image_becomes_primary(self):
        image = ProductImage.objects.create(product=self.product, image="products/first.jpg")
        image.refresh_from_db()
        self.assertTrue(image.is_primary)

    def test_second_image_not_primary_by_default(self):
        ProductImage.objects.create(product=self.product, image="products/first.jpg")
        second = ProductImage.objects.create(product=self.product, image="products/second.jpg")
        self.assertFalse(second.is_primary)
