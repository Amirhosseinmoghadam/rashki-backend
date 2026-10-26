from django.test import TestCase
from categories.models import Category
from categories.api.v1.serializers import (
    CategorySerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    CategoryTreeSerializer,
)


class CategorySerializerTests(TestCase):
    def setUp(self):
        self.root = Category.objects.create(name='سیستم ترمز')
        self.child = Category.objects.create(name='دیسک ترمز', parent=self.root)
        self.disabled = Category.objects.create(name='پنهان', parent=self.root, is_active=False)

    def test_list_children_only_active_ids(self):
        data = CategorySerializer(self.root).data
        self.assertIn(self.child.pk, data['children'])
        self.assertNotIn(self.disabled.pk, data['children'])

    def test_list_parent_is_id(self):
        self.assertEqual(CategorySerializer(self.child).data['parent'], self.root.pk)

    def test_detail_children_are_objects(self):
        data = CategoryDetailSerializer(self.root).data
        self.assertEqual([item['id'] for item in data['children']], [self.child.pk])

    def test_detail_parent_is_object(self):
        self.assertEqual(CategoryDetailSerializer(self.child).data['parent']['id'], self.root.pk)

    def test_detail_inactive_parent_hidden(self):
        root = Category.objects.create(name='غیرفعال', is_active=False)
        child = Category.objects.create(name='فرزند', parent=root)
        self.assertIsNone(CategoryDetailSerializer(child).data['parent'])

    def test_create_trims_name(self):
        serializer = CategoryCreateUpdateSerializer(data={'name': '  زنجیر  '})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['name'], 'زنجیر')

    def test_blank_name_rejected(self):
        serializer = CategoryCreateUpdateSerializer(data={'name': '  '})
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_inactive_parent_rejected(self):
        root = Category.objects.create(name='خاموش', is_active=False)
        serializer = CategoryCreateUpdateSerializer(data={'name': 'فرزند', 'parent': root.pk})
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)

    def test_self_parent_rejected(self):
        serializer = CategoryCreateUpdateSerializer(instance=self.root, data={'parent': self.root.pk}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)

    def test_cycle_parent_rejected(self):
        serializer = CategoryCreateUpdateSerializer(instance=self.root, data={'parent': self.child.pk}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)

    def test_slug_read_only(self):
        serializer = CategoryCreateUpdateSerializer(instance=self.root, data={'slug': 'changed'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('slug', serializer.validated_data)

    def test_tree_recursively_serializes_dicts(self):
        data = CategoryTreeSerializer({'id': 1, 'name': 'A', 'slug': 'a', 'image': None,
            'children': [{'id': 2, 'name': 'B', 'slug': 'b', 'image': None, 'children': []}]}).data
        self.assertEqual(data['children'][0]['id'], 2)
