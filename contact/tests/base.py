from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from contact.models import ContactRequest


def payload(**changes):
    data = {
        "first_name": "علی", "last_name": "احمدی",
        "phone_number": "09123456789",
        "subject": ContactRequest.Subject.PRICE_INQUIRY,
        "description": "لطفاً قیمت محصول را اعلام کنید.",
    }
    data.update(changes)
    return data


def make_request(**changes):
    return ContactRequest.objects.create(**payload(**changes))


def make_user(phone, staff=False):
    user = get_user_model().objects.create(phone_number=phone, is_staff=staff)
    user.set_unusable_password()
    user.save(update_fields=["password"])
    return user


class ContactAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.create_url = reverse("contact_api_v1:contact-create")
        self.list_url = reverse("contact_api_v1:contact-admin-list")

    def detail_url(self, pk):
        return reverse("contact_api_v1:contact-admin-detail", kwargs={"pk": pk})
