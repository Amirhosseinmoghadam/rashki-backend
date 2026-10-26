from brands.models import Brand
from .base import BrandAPITestBase


class BrandViewTests(BrandAPITestBase):
    def test_public_list_returns_only_active(self):
        response = self.client.get(self.list_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'Honda')

    def test_search_name(self):
        response = self.client.get(self.list_url(), {'search': 'HON'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_search_description(self):
        response = self.client.get(self.list_url(), {'search': 'parts'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_search_no_match(self):
        response = self.client.get(self.list_url(), {'search': 'unknown'})
        self.assertEqual(response.data['count'], 0)

    def test_public_detail_active(self):
        response = self.client.get(self.detail_url(self.active))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['slug'], self.active.slug)

    def test_public_detail_inactive_not_found(self):
        response = self.client.get(self.detail_url(self.inactive))
        self.assertEqual(response.status_code, 404)

    def test_admin_create_generates_slug(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url(), {'name': 'Suzuki'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['data']['slug'], 'suzuki')
        self.assertTrue(Brand.objects.filter(name='Suzuki').exists())

    def test_admin_create_duplicate_returns_400(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url(), {'name': 'honda'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_put_updates_brand(self):
        self.client.force_authenticate(self.staff)
        response = self.client.put(self.detail_url(self.active), {'name': 'Honda New'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.active.refresh_from_db()
        self.assertEqual(self.active.name, 'Honda New')

    def test_admin_patch_inactive_brand(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(self.detail_url(self.inactive), {'is_active': True}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.inactive.refresh_from_db()
        self.assertTrue(self.inactive.is_active)

    def test_admin_delete(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(self.detail_url(self.inactive))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(Brand.objects.filter(pk=self.inactive.pk).exists())

    def test_missing_brand_returns_404(self):
        response = self.client.get(self.detail_url(type('Obj', (), {'pk': 999999})()))
        self.assertEqual(response.status_code, 404)
