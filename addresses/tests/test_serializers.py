from addresses.api.v1.serializers import AddressCreateSerializer,AddressUpdateSerializer,AddressSerializer
from .base import AddressTestBase

class AddressSerializerTests(AddressTestBase):
    def test_valid_address_create(self):
        serializer=AddressCreateSerializer(data=self.payload())
        self.assertTrue(serializer.is_valid(),serializer.errors)

    def test_reject_city_from_other_province(self):
        serializer=AddressCreateSerializer(data=self.payload(city=self.other_city.pk))
        self.assertFalse(serializer.is_valid())
        self.assertIn("city",serializer.errors)

    def test_reject_bad_mobile_and_postal_code(self):
        serializer=AddressCreateSerializer(data=self.payload(mobile_number="123",postal_code="abc"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("mobile_number",serializer.errors)
        self.assertIn("postal_code",serializer.errors)

    def test_required_fields_on_create(self):
        serializer=AddressCreateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        for name in ("first_name","last_name","mobile_number","postal_code","postal_address"):
            self.assertIn(name,serializer.errors)

    def test_partial_update_uses_existing_province_to_check_city(self):
        address=self.make_address()
        serializer=AddressUpdateSerializer(address,data={"city":self.other_city.pk},partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("city",serializer.errors)

    def test_read_serializer_adds_location_names(self):
        data=AddressSerializer(self.make_address()).data
        self.assertEqual(data["province_name"],self.province.name)
        self.assertEqual(data["city_name"],self.city.name)
