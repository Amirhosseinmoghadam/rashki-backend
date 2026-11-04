from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from products.api.v1.views import ProductViewSet
from products.models import Product
from categories.models import Category
from .base import ProductFixture

class ProductVisibilityTests(ProductFixture):
    def _get_queryset(self, action="list"):
        view = ProductViewSet()
        view.action = action
        view.request = Request(APIRequestFactory().get("/products/"))
        return view.get_queryset()

    def test_active_product_is_public(self):
        self.assertIn(self.product, self._get_queryset())

    def test_draft_product_is_private(self):
        self.product.status = Product.Status.DRAFT
        self.product.save()
        self.assertNotIn(self.product, self._get_queryset())

    def test_archived_product_is_private(self):
        self.product.status = Product.Status.ARCHIVED
        self.product.save()
        self.assertNotIn(self.product, self._get_queryset())

    def test_inactive_category_hides_product(self):
        self.category.is_active = False
        self.category.save()
        self.assertNotIn(self.product, self._get_queryset())

    def test_inactive_ancestor_hides_product(self):
        parent = Category.objects.create(name="والد غیرفعال", is_active=False)
        self.category.parent = parent
        self.category.save()
        self.assertNotIn(self.product, self._get_queryset())

    def test_admin_edit_queryset_includes_draft(self):
        self.product.status = Product.Status.DRAFT
        self.product.save()
        self.assertIn(self.product, self._get_queryset(action="update"))
