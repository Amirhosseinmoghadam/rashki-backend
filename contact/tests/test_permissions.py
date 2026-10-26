from unittest.mock import patch
from .base import ContactAPITestCase,make_request,make_user,payload
from contact.models import ContactRequest


class ContactPermissionsTests(ContactAPITestCase):
    def test_anonymous_cannot_list_or_read_admin_detail(self):
        item=make_request()
        for url in (self.list_url,self.detail_url(item.pk)):
            with self.subTest(url=url):
                self.assertIn(self.client.get(url).status_code,(401,403))

    def test_regular_user_cannot_access_admin_apis(self):
        self.client.force_authenticate(make_user("09111111111"))
        item=make_request()
        self.assertEqual(self.client.get(self.list_url).status_code,403)
        self.assertEqual(self.client.get(self.detail_url(item.pk)).status_code,403)
        self.assertEqual(self.client.patch(self.detail_url(item.pk),{"is_read":True},format="json").status_code,403)
        item.refresh_from_db();self.assertFalse(item.is_read)

    def test_staff_can_access_admin_endpoints(self):
        self.client.force_authenticate(make_user("09222222222",staff=True))
        item=make_request()
        self.assertEqual(self.client.get(self.list_url).status_code,200)
        self.assertEqual(self.client.get(self.detail_url(item.pk)).status_code,200)

    def test_public_create_stays_available_to_regular_user(self):
        self.client.force_authenticate(make_user("09333333333"))
        with patch("contact.throttles.ContactRequestThrottle.allow_request",return_value=True):
            response=self.client.post(self.create_url,payload(),format="json")
        self.assertEqual(response.status_code,201,response.data)
        self.assertEqual(ContactRequest.objects.count(),1)
