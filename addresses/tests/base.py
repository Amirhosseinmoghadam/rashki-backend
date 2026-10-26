from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from addresses.models import Address, City, Province

class AddressTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create(phone_number="09120000001", is_active=True)
        cls.other = User.objects.create(phone_number="09120000002", is_active=True)
        cls.province = Province.objects.create(name="تهران")
        cls.city = City.objects.create(province=cls.province, name="تهران")
        cls.other_province = Province.objects.create(name="البرز")
        cls.other_city = City.objects.create(province=cls.other_province, name="کرج")

    def payload(self, **overrides):
        data = dict(first_name="علی",last_name="رضایی",mobile_number="09120000003",
                    phone_number="02112345678",province=self.province.pk,city=self.city.pk,
                    postal_code="1234567890",postal_address="خیابان نمونه")
        data.update(overrides)
        return data

    def make_address(self, user=None, **overrides):
        values = dict(first_name="علی",last_name="رضایی",mobile_number="09120000003",
                      province=self.province,city=self.city,postal_code="1234567890",
                      postal_address="خیابان نمونه",is_default=False)
        values.update(overrides)
        return Address.objects.create(user=user or self.user, **values)

    def authenticated_client(self, user=None):
        client=APIClient()
        client.force_authenticate(user=user or self.user)
        return client
