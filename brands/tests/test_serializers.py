from django.test import TestCase
from brands.models import Brand
from brands.api.v1.serializers import BrandListSerializer, BrandDetailSerializer, BrandCreateUpdateSerializer


class BrandSerializerTests(TestCase):
    def test_create_normalizes_whitespace(self):
        serializer = BrandCreateUpdateSerializer(data={'name': '  Honda   Motor  '})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        brand = serializer.save()
        self.assertEqual(brand.name, 'Honda Motor')
        self.assertEqual(brand.slug, 'honda-motor')

    def test_empty_name_rejected(self):
        serializer = BrandCreateUpdateSerializer(data={'name': '  '})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_duplicate_name_case_insensitive(self):
        Brand.objects.create(name='Honda')
        serializer = BrandCreateUpdateSerializer(data={'name': 'honda'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_update_same_name_is_allowed(self):
        brand = Brand.objects.create(name='Honda')
        serializer = BrandCreateUpdateSerializer(instance=brand, data={'name': 'Honda'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_description_is_trimmed(self):
        serializer = BrandCreateUpdateSerializer(data={'name': 'Honda', 'description': '  hello  '})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['description'], 'hello')

    def test_invalid_website_rejected(self):
        serializer = BrandCreateUpdateSerializer(data={'name': 'Honda', 'website': 'invalid-url'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('website', serializer.errors)

    def test_slug_is_read_only(self):
        serializer = BrandCreateUpdateSerializer(data={'name': 'Honda', 'slug': 'injected'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        brand = serializer.save()
        self.assertEqual(brand.slug, 'honda')

    def test_list_serializer_has_only_public_list_fields(self):
        brand = Brand.objects.create(name='Honda')
        self.assertEqual(set(BrandListSerializer(brand).data), {'id', 'name', 'slug', 'logo', 'description'})

    def test_detail_serializer_includes_status_and_timestamps(self):
        brand = Brand.objects.create(name='Honda')
        data = BrandDetailSerializer(brand).data
        self.assertTrue({'website', 'is_active', 'created_at', 'updated_at'}.issubset(data))
