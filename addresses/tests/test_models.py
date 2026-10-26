from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from addresses.models import Address, City, Province
from .base import AddressTestBase

class LocationModelTests(AddressTestBase):
    def test_province_string(self):
        self.assertEqual(str(self.province), "تهران")

    def test_city_string(self):
        self.assertEqual(str(self.city), "تهران (تهران)")

    def test_same_city_name_allowed_in_another_province(self):
        City.objects.create(province=self.other_province, name=self.city.name)

    def test_city_name_unique_inside_province(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                City.objects.create(province=self.province, name=self.city.name)

    def test_province_name_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Province.objects.create(name=self.province.name)

class AddressModelTests(AddressTestBase):
    def test_string_representation(self):
        self.assertEqual(str(self.make_address()), "علی رضایی - تهران")

    def test_invalid_mobile_and_postal_code(self):
        address=self.make_address(mobile_number="123",postal_code="bad")
        with self.assertRaises(ValidationError):
            address.full_clean()

    def test_only_one_default_per_user(self):
        self.make_address(is_default=True)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_address(is_default=True)

    def test_different_users_can_have_defaults(self):
        self.make_address(is_default=True)
        self.make_address(user=self.other,is_default=True)

    def test_deleting_province_with_address_is_protected(self):
        self.make_address()
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.province.delete()
