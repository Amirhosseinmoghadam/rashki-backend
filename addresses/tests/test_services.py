from django.contrib.auth import get_user_model
from django.test import TestCase

from addresses.models import City, Province
from addresses.services import (
    AddressServiceError,
    create_address,
    delete_address,
    set_default_address,
    update_address,
)


class AddressServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create(
            phone_number="09120000001",
            is_active=True,
        )

        self.province = Province.objects.create(
            name="استان تست",
        )

        self.city = City.objects.create(
            province=self.province,
            name="شهر تست",
        )

    def _data(
        self,
        *,
        suffix,
        is_default=False,
    ):
        return {
            "first_name": "کاربر",
            "last_name": "تست",
            "mobile_number": (
                f"0912000000{suffix}"
            ),
            "phone_number": "02112345678",
            "province": self.province,
            "city": self.city,
            "postal_code": (
                f"123456789{suffix}"
            ),
            "postal_address": (
                f"آدرس تست {suffix}"
            ),
            "is_default": is_default,
        }

    def test_first_address_becomes_default(self):
        address = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=1,
            ),
        )

        self.assertTrue(
            address.is_default
        )

    def test_setting_new_default_unsets_old(self):
        first = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=1,
            ),
        )

        second = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=2,
            ),
        )

        set_default_address(
            address=second,
        )

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertFalse(
            first.is_default
        )

        self.assertTrue(
            second.is_default
        )

    def test_default_cannot_be_unset_directly(self):
        address = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=1,
            ),
        )

        with self.assertRaises(
            AddressServiceError
        ):
            update_address(
                address=address,
                validated_data={
                    "is_default": False,
                },
            )

    def test_delete_default_promotes_newest(self):
        first = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=1,
            ),
        )

        second = create_address(
            user=self.user,
            validated_data=self._data(
                suffix=2,
            ),
        )

        delete_address(
            address=first,
        )

        second.refresh_from_db()

        self.assertTrue(
            second.is_default
        )
