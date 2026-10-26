from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from categories.models import Category


class CategoryAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Category.objects.create(name='قطعات موتور', description='قطعات اصلی')
        cls.child = Category.objects.create(name='لنت ترمز', parent=cls.root)
        cls.inactive = Category.objects.create(name='مخفی', is_active=False)
        cls.hidden_child = Category.objects.create(name='فرزند مخفی', parent=cls.inactive)
        User = get_user_model()
        cls.staff = User.objects.create_user(phone_number='09120000001', password='TestPass123!')
        cls.staff.is_staff = True
        cls.staff.save(update_fields=['is_staff'])
        cls.user = User.objects.create_user(phone_number='09120000002', password='TestPass123!')

    @staticmethod
    def list_url():
        return reverse('category-list')

    @staticmethod
    def detail_url(pk):
        return reverse('category-detail', args=[pk])

    @staticmethod
    def tree_url():
        return reverse('category-tree')
