from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAdminUser
from products.api.v1.views import ProductViewSet, ProductImageViewSet
from django.test import SimpleTestCase

class ProductPermissionContractTests(SimpleTestCase):
    def test_public_list_permission(self):
        view = ProductViewSet()
        view.action = "list"
        self.assertIsInstance(view.get_permissions()[0], AllowAny)

    def test_public_retrieve_permission(self):
        view = ProductViewSet()
        view.action = "retrieve"
        self.assertIsInstance(view.get_permissions()[0], AllowAny)

    def test_create_requires_admin(self):
        view = ProductViewSet()
        view.action = "create"
        self.assertIsInstance(view.get_permissions()[0], IsAdminUser)

    def test_update_requires_admin(self):
        view = ProductViewSet()
        view.action = "update"
        self.assertIsInstance(view.get_permissions()[0], IsAdminUser)

    def test_delete_requires_admin(self):
        view = ProductViewSet()
        view.action = "destroy"
        self.assertIsInstance(view.get_permissions()[0], IsAdminUser)

    def test_image_endpoints_admin_only(self):
        self.assertIn(IsAdminUser, ProductImageViewSet.permission_classes)
