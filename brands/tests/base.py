from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from brands.models import Brand


class BrandAPITestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user(phone_number='09120000001', password='TestPass123!')
        cls.staff.is_staff = True
        cls.staff.save(update_fields=['is_staff'])
        cls.customer = User.objects.create_user(phone_number='09120000002', password='TestPass123!')
        cls.active = Brand.objects.create(name='Honda', description='Motorcycle parts')
        cls.inactive = Brand.objects.create(name='Yamaha', is_active=False)

    @staticmethod
    def list_url():
        return reverse('brands_api_v1:brand-list')

    @staticmethod
    def detail_url(brand):
        return reverse('brands_api_v1:brand-detail', args=[brand.pk])
