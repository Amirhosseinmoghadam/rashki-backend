from categories.models import Category
from .base import CategoryAPITestCase


class CategoryViewTests(CategoryAPITestCase):
    def test_list_is_public(self):
        response = self.client.get(self.list_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIsInstance(response.data['data'], list)

    def test_public_list_excludes_inactive_ancestors_and_descendants(self):
        response = self.client.get(self.list_url())
        ids = {item['id'] for item in response.data['data']}
        self.assertIn(self.root.pk, ids)
        self.assertIn(self.child.pk, ids)
        self.assertNotIn(self.inactive.pk, ids)
        self.assertNotIn(self.hidden_child.pk, ids)

    def test_root_filter(self):
        response = self.client.get(self.list_url(), {'parent': 'root'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['data']], [self.root.pk])

    def test_parent_id_filter(self):
        response = self.client.get(self.list_url(), {'parent': str(self.root.pk)})
        self.assertEqual([item['id'] for item in response.data['data']], [self.child.pk])

    def test_invalid_parent_filter_returns_empty(self):
        response = self.client.get(self.list_url(), {'parent': 'invalid'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data'], [])

    def test_search_name(self):
        response = self.client.get(self.list_url(), {'search': 'لنت'})
        self.assertEqual([item['id'] for item in response.data['data']], [self.child.pk])

    def test_search_description(self):
        response = self.client.get(self.list_url(), {'search': 'اصلی'})
        self.assertEqual([item['id'] for item in response.data['data']], [self.root.pk])

    def test_detail_public(self):
        response = self.client.get(self.detail_url(self.root.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['id'], self.root.pk)

    def test_inactive_detail_not_found(self):
        response = self.client.get(self.detail_url(self.inactive.pk))
        self.assertEqual(response.status_code, 404)

    def test_hidden_descendant_detail_not_found(self):
        response = self.client.get(self.detail_url(self.hidden_child.pk))
        self.assertEqual(response.status_code, 404)

    def test_tree_nested_and_hidden_filtered(self):
        response = self.client.get(self.tree_url())
        self.assertEqual(response.status_code, 200)
        tree = response.data['data']
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['id'], self.root.pk)
        self.assertEqual([node['id'] for node in tree[0]['children']], [self.child.pk])

    def test_admin_create_category_and_auto_slug(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url(), {'name': 'دسته تست جدید'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data['data']['slug'])
        self.assertTrue(Category.objects.filter(name='دسته تست جدید').exists())

    def test_admin_patch_preserves_slug(self):
        old_slug = self.root.slug
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.detail_url(self.root.pk), {'name': 'نام جدید'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.root.refresh_from_db()
        self.assertEqual(self.root.slug, old_slug)

    def test_admin_put_category(self):
        self.client.force_authenticate(self.staff)
        response = self.client.put(self.detail_url(self.child.pk), {'name': 'لنت اصلاح شده', 'parent': self.root.pk}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, 'لنت اصلاح شده')

    def test_admin_delete_leaf(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(self.detail_url(self.child.pk))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(Category.objects.filter(pk=self.child.pk).exists())

    def test_admin_delete_parent_with_children_returns_conflict(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(self.detail_url(self.root.pk))
        self.assertEqual(response.status_code, 409, response.data)
        self.assertTrue(Category.objects.filter(pk=self.root.pk).exists())
