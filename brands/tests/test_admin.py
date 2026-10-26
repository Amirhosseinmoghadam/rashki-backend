from django.test import TestCase
from django.contrib import admin
from brands.admin import BrandAdmin
from brands.models import Brand


class BrandAdminTests(TestCase):
    def test_registered_in_admin(self):
        self.assertIsInstance(admin.site._registry[Brand], BrandAdmin)

    def test_preview_without_logo(self):
        brand = Brand.objects.create(name='Honda')
        admin_instance = admin.site._registry[Brand]
        self.assertEqual(admin_instance.logo_preview(brand), 'بدون لوگو')
