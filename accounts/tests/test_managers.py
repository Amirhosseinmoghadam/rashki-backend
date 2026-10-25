from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user_trims_phone_and_hashes_password(self):
        user = self.User.objects.create_user(' 09123456789 ', password='TestPass123!')
        self.assertEqual(user.phone_number, '09123456789')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertNotEqual(user.password, 'TestPass123!')

    def test_create_user_requires_phone(self):
        with self.assertRaises(ValueError):
            self.User.objects.create_user('')

    def test_create_superuser(self):
        user = self.User.objects.create_superuser('09123456789', 'TestPass123!')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_superuser_requires_password(self):
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser('09123456789')

    def test_superuser_rejects_missing_permissions(self):
        for field in ('is_staff', 'is_superuser'):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self.User.objects.create_superuser(
                        '09123456789', 'TestPass123!', **{field: False}
                    )
