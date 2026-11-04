from django.urls import resolve, reverse
from django.test import SimpleTestCase


class MotorcycleUrlTests(SimpleTestCase):
    def test_brand_list_route(self):
        match = resolve("/api/v1/motorcycles/motorcycle-brands/")
        self.assertEqual(match.url_name, "motorcycle-brand-list")

    def test_model_list_route(self):
        match = resolve("/api/v1/motorcycles/motorcycles/")
        self.assertEqual(match.url_name, "motorcycle-list")

    def test_model_detail_route(self):
        match = resolve("/api/v1/motorcycles/motorcycles/123/")
        self.assertEqual(match.url_name, "motorcycle-detail")
