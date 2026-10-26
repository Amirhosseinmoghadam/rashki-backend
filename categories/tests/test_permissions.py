from .base import CategoryAPITestCase


class CategoryPermissionTests(CategoryAPITestCase):
    def test_anonymous_cannot_create(self):
        response = self.client.post(self.list_url(), {'name': 'بدون ورود'}, format='json')
        self.assertIn(response.status_code, (401, 403))

    def test_regular_user_cannot_create(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.list_url(), {'name': 'غیرمجاز'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_update(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.detail_url(self.root.pk), {'name': 'غیرمجاز'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_delete(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.detail_url(self.child.pk))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_create(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url(), {'name': 'دسترسی مدیر'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
