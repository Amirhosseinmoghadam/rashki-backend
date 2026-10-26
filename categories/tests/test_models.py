from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from categories.models import Category


class CategoryModelTests(TestCase):
    def test_slug_generated_automatically(self):
        category = Category.objects.create(name='روغن موتور')
        self.assertTrue(category.slug)

    def test_slug_unchanged_after_renaming(self):
        category = Category.objects.create(name='ترمز')
        original = category.slug
        category.name = 'ترمز جلو'
        category.save()
        self.assertEqual(category.slug, original)

    def test_duplicate_names_generate_distinct_slugs(self):
        first = Category.objects.create(name='فیلتر هوا')
        second = Category.objects.create(name='فیلتر هوا')
        self.assertNotEqual(first.slug, second.slug)

    def test_default_active(self):
        self.assertTrue(Category.objects.create(name='زنجیر').is_active)

    def test_children_reverse_relation(self):
        parent = Category.objects.create(name='بدنه')
        child = Category.objects.create(name='قاب', parent=parent)
        self.assertIn(child, parent.children.all())

    def test_direct_self_parent_rejected(self):
        category = Category.objects.create(name='فرمان')
        category.parent = category
        with self.assertRaises(ValidationError):
            category.save()

    def test_ancestor_cycle_rejected(self):
        root = Category.objects.create(name='برق')
        child = Category.objects.create(name='باتری', parent=root)
        grandchild = Category.objects.create(name='باتری کوچک', parent=child)
        root.parent = grandchild
        with self.assertRaises(ValidationError):
            root.save()

    def test_parent_delete_protected(self):
        root = Category.objects.create(name='کمک فنر')
        Category.objects.create(name='کمک جلو', parent=root)
        with self.assertRaises(ProtectedError):
            root.delete()

    def test_nested_string_representation(self):
        root = Category.objects.create(name='چرخ')
        child = Category.objects.create(name='رینگ', parent=root)
        self.assertEqual(str(child), 'چرخ → رینگ')
