from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils.text import slugify
from brands.models import Brand


class BrandModelTests(TestCase):
    def test_slug_generated_automatically(self):
        brand = Brand.objects.create(name='Honda Motor')
        self.assertEqual(brand.slug, 'honda-motor')

    def test_persian_slug_normalization(self):
        brand = Brand.objects.create(name='هوندا ۱۲۵')
        self.assertEqual(brand.slug, 'هوندا-125')

    def test_slug_collisions_get_suffix(self):
        Brand.objects.create(name='Honda Motor')
        second = Brand.objects.create(name='honda motor')
        self.assertEqual(second.slug, 'honda-motor-2')

    def test_explicit_slug_preserved(self):
        brand = Brand.objects.create(name='Honda', slug='custom-honda')
        self.assertEqual(brand.slug, 'custom-honda')

    def test_slug_does_not_change_after_rename(self):
        brand = Brand.objects.create(name='Honda')
        brand.name = 'Honda Updated'
        brand.save()
        self.assertEqual(brand.slug, 'honda')

    def test_name_must_be_unique_in_database(self):
        Brand.objects.create(name='Honda')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Brand.objects.create(name='Honda')

    def test_default_active_and_string_representation(self):
        brand = Brand.objects.create(name='Suzuki')
        self.assertTrue(brand.is_active)
        self.assertEqual(str(brand), 'Suzuki')

    def test_default_ordering(self):
        Brand.objects.create(name='Yamaha')
        Brand.objects.create(name='Honda')
        self.assertEqual(list(Brand.objects.values_list('name', flat=True)), ['Honda', 'Yamaha'])

    def test_timestamps_are_set(self):
        brand = Brand.objects.create(name='Kawasaki')
        self.assertIsNotNone(brand.created_at)
        self.assertIsNotNone(brand.updated_at)
