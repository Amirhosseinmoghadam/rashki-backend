from addresses.selectors import get_provinces,get_cities_for_province,get_user_addresses,get_user_address
from .base import AddressTestBase

class AddressSelectorTests(AddressTestBase):
    def test_provinces_sorted_by_name(self):
        self.assertEqual(list(get_provinces().values_list("name",flat=True)), ["البرز","تهران"])

    def test_cities_filtered_by_province(self):
        self.assertEqual(list(get_cities_for_province(province_id=self.province.pk)),[self.city])

    def test_user_addresses_are_private_and_default_first(self):
        first=self.make_address()
        default=self.make_address(is_default=True)
        self.make_address(user=self.other)
        self.assertEqual(list(get_user_addresses(user=self.user)),[default,first])

    def test_lookup_does_not_expose_other_users(self):
        address=self.make_address(user=self.other)
        self.assertIsNone(get_user_address(user=self.user,pk=address.pk))
