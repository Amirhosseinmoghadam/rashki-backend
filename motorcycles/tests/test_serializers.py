from motorcycles.api.v1.serializers import (
    MotorcycleBrandCreateUpdateSerializer, MotorcycleModelCreateUpdateSerializer,
    MotorcycleModelListSerializer, MotorcycleModelDetailSerializer,
    MotorcycleBrandListSerializer,
)
from .base import MotorcycleTestBase


class MotorcycleSerializerTests(MotorcycleTestBase):
    def test_brand_valid(self):
        s = MotorcycleBrandCreateUpdateSerializer(data={"name": "Kawasaki"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_brand_duplicate_case_insensitive(self):
        s = MotorcycleBrandCreateUpdateSerializer(data={"name": "hONDA"})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_brand_blank_name(self):
        s = MotorcycleBrandCreateUpdateSerializer(data={"name": "  "})
        self.assertFalse(s.is_valid())

    def test_brand_slug_readonly(self):
        s = MotorcycleBrandCreateUpdateSerializer(data={"name": "Kawasaki", "slug": "fake"})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("slug", s.validated_data)

    def test_brand_list_fields(self):
        data = MotorcycleBrandListSerializer(self.brand).data
        self.assertIn("slug", data)
        self.assertIn("logo", data)

    def test_model_valid(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.brand.pk, "name": "CB 650", "engine_volume": 650})
        self.assertTrue(s.is_valid(), s.errors)

    def test_model_unknown_brand(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": 999999, "name": "CB 650"})
        self.assertFalse(s.is_valid())
        self.assertIn("brand", s.errors)

    def test_model_duplicate_under_same_brand(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.brand.pk, "name": "cbr 250"})
        self.assertFalse(s.is_valid())
        self.assertIn("name", s.errors)

    def test_model_same_name_different_brand(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.other_brand.pk, "name": "CBR 250"})
        self.assertTrue(s.is_valid(), s.errors)

    def test_model_invalid_production_year_range(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.brand.pk, "name": "Test", "production_start_year": 2024, "production_end_year": 2020})
        self.assertFalse(s.is_valid())
        self.assertIn("production_end_year", s.errors)

    def test_partial_update_keeps_existing_year_for_validation(self):
        s = MotorcycleModelCreateUpdateSerializer(self.model, data={"production_end_year": 2010}, partial=True)
        self.assertFalse(s.is_valid())

    def test_model_zero_engine_volume(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.brand.pk, "name": "Test", "engine_volume": 0})
        self.assertFalse(s.is_valid())

    def test_nested_brand_in_model_list(self):
        data = MotorcycleModelListSerializer(self.model).data
        self.assertEqual(data["brand"]["id"], self.brand.pk)

    def test_description_in_detail_not_list(self):
        self.assertIn("description", MotorcycleModelDetailSerializer(self.model).data)
        self.assertNotIn("description", MotorcycleModelListSerializer(self.model).data)

    def test_model_slug_read_only(self):
        s = MotorcycleModelCreateUpdateSerializer(data={"brand": self.brand.pk, "name": "New", "slug": "override"})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("slug", s.validated_data)
