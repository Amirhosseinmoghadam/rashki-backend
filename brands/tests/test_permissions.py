from .base import BrandAPITestBase


class BrandPermissionsTests(BrandAPITestBase):
    def test_anonymous_can_list_and_retrieve(self):
        self.assertEqual(self.client.get(self.list_url()).status_code, 200)
        self.assertEqual(self.client.get(self.detail_url(self.active)).status_code, 200)

    def test_anonymous_cannot_write(self):
        checks = [
            ('post', self.list_url(), {'name': 'Suzuki'}),
            ('put', self.detail_url(self.active), {'name': 'Changed'}),
            ('patch', self.detail_url(self.active), {'name': 'Changed'}),
            ('delete', self.detail_url(self.active), None),
        ]
        for method, url, data in checks:
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, data=data, format='json')
                self.assertIn(response.status_code, (401, 403))

    def test_regular_user_cannot_write(self):
        self.client.force_authenticate(self.customer)
        checks = [
            ('post', self.list_url(), {'name': 'Suzuki'}),
            ('put', self.detail_url(self.active), {'name': 'Changed'}),
            ('patch', self.detail_url(self.active), {'name': 'Changed'}),
            ('delete', self.detail_url(self.active), None),
        ]
        for method, url, data in checks:
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, data=data, format='json')
                self.assertEqual(response.status_code, 403)
