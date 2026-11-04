from django.test import SimpleTestCase
from products.api.v1.urls import router
from products.api.v1.views import ProductViewSet, ProductImageViewSet, ProductAttributeViewSet

class ProductRouterTests(SimpleTestCase):
    def test_product_route_registered(self):
        entries = {prefix: view for prefix, view, basename in router.registry}
        self.assertIs(entries["products"], ProductViewSet)

    def test_images_route_registered(self):
        entries = {prefix: view for prefix, view, basename in router.registry}
        self.assertIs(entries["product-images"], ProductImageViewSet)

    def test_attributes_route_registered(self):
        entries = {prefix: view for prefix, view, basename in router.registry}
        self.assertIs(entries["product-attributes"], ProductAttributeViewSet)
