from unittest.mock import patch
from rest_framework import status
from .base import ContactAPITestCase, make_request, payload, make_user
from contact.models import ContactRequest


class ContactCreateViewTests(ContactAPITestCase):
    def test_anonymous_create(self):
        with patch("contact.throttles.ContactRequestThrottle.allow_request",return_value=True):
            response=self.client.post(self.create_url,payload(),format="json")
        self.assertEqual(response.status_code,status.HTTP_201_CREATED,response.data)
        self.assertTrue(response.data["success"])
        self.assertEqual(ContactRequest.objects.count(),1)
        self.assertEqual(response.data["data"]["id"],ContactRequest.objects.get().pk)

    def test_invalid_payload_is_400(self):
        with patch("contact.throttles.ContactRequestThrottle.allow_request",return_value=True):
            response=self.client.post(self.create_url,payload(phone_number="bad"),format="json")
        self.assertEqual(response.status_code,400)
        self.assertFalse(ContactRequest.objects.exists())

    def test_duplicate_is_400(self):
        make_request()
        with patch("contact.throttles.ContactRequestThrottle.allow_request",return_value=True):
            response=self.client.post(self.create_url,payload(),format="json")
        self.assertEqual(response.status_code,400)
        self.assertEqual(ContactRequest.objects.count(),1)


class ContactAdminViewsTests(ContactAPITestCase):
    def setUp(self):
        super().setUp()
        self.admin=make_user("09111111111",staff=True)
        self.client.force_authenticate(self.admin)

    def test_list_pagination_shape(self):
        make_request()
        response=self.client.get(self.list_url)
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(response.data["data"]["total_objects"],1)
        self.assertEqual(len(response.data["data"]["results"]),1)

    def test_list_pagination_second_page(self):
        for index in range(21):
            make_request(phone_number=f"09{index:09d}")
        response=self.client.get(self.list_url,{"page":2})
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(response.data["data"]["total_objects"],21)
        self.assertEqual(len(response.data["data"]["results"]),1)

    def test_detail(self):
        item=make_request()
        response=self.client.get(self.detail_url(item.pk))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data["data"]["id"],item.pk)

    def test_missing_detail_is_404(self):
        response=self.client.get(self.detail_url(999999))
        self.assertEqual(response.status_code,404)

    def test_patch_read_and_unread(self):
        item=make_request()
        for value in (True,False):
            with self.subTest(value=value):
                response=self.client.patch(self.detail_url(item.pk),{"is_read":value},format="json")
                self.assertEqual(response.status_code,200,response.data)
                item.refresh_from_db()
                self.assertEqual(item.is_read,value)

    def test_patch_cannot_change_description(self):
        item=make_request()
        response=self.client.patch(self.detail_url(item.pk),{"description":"hacked","is_read":True},format="json")
        self.assertEqual(response.status_code,200,response.data)
        item.refresh_from_db()
        self.assertNotEqual(item.description,"hacked")

    def test_put_and_delete_not_allowed(self):
        item=make_request()
        self.assertEqual(self.client.put(self.detail_url(item.pk),{},format="json").status_code,405)
        self.assertEqual(self.client.delete(self.detail_url(item.pk)).status_code,405)
