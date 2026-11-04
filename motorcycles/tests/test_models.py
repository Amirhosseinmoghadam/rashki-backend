from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from motorcycles.models import MotorcycleBrand, MotorcycleModel
from .base import MotorcycleTestBase


class MotorcycleModelTests(MotorcycleTestBase):
    def test_brand_slug_generated(self):
        self.assertTrue(self.brand.slug)

    def test_model_slug_generated(self):
        self.assertTrue(self.model.slug)

    def test_model_slug_contains_brand_context(self):
        self.assertNotEqual(self.model.slug, self.other_model.slug)

    def test_brand_string(self):
        self.assertEqual(str(self.brand), "Honda")

    def test_model_string(self):
        self.assertEqual(str(self.model), "Honda CBR 250")

    def test_brand_name_trimmed_on_save(self):
        brand = MotorcycleBrand.objects.create(name="  Suzuki  ")
        self.assertEqual(brand.name, "Suzuki")

    def test_model_name_trimmed_on_save(self):
        model = MotorcycleModel.objects.create(brand=self.brand, name="  CB 500  ")
        self.assertEqual(model.name, "CB 500")

    def test_brand_case_insensitive_duplicate_validation(self):
        with self.assertRaises(ValidationError):
            MotorcycleBrand(name="honda").full_clean()

    def test_model_duplicate_for_same_brand_validation(self):
        with self.assertRaises(ValidationError):
            MotorcycleModel(brand=self.brand, name="cbr 250").full_clean()

    def test_same_name_under_another_brand_allowed(self):
        MotorcycleModel(brand=self.other_brand, name="CBR 250").full_clean()

    def test_end_year_before_start_rejected(self):
        with self.assertRaises(ValidationError):
            MotorcycleModel(brand=self.brand, name="New", production_start_year=2025, production_end_year=2020).full_clean()

    def test_zero_engine_volume_rejected(self):
        with self.assertRaises(ValidationError):
            MotorcycleModel(brand=self.brand, name="New", engine_volume=0).full_clean()

    def test_valid_production_years(self):
        MotorcycleModel(brand=self.brand, name="New", production_start_year=2020, production_end_year=2025, engine_volume=100).full_clean()

    def test_brand_with_models_protected_from_delete(self):
        with self.assertRaises(ProtectedError):
            self.brand.delete()

    def test_slug_remains_after_name_update(self):
        before = self.model.slug
        self.model.name = "CBR New"
        self.model.save()
        self.assertEqual(self.model.slug, before)
