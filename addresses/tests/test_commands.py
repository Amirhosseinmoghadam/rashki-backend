from io import StringIO
from django.core.management import call_command
from django.test import SimpleTestCase
from addresses.management.commands.sync_addresses_from_tipax import normalize_location_name,parse_tipax_state,parse_tipax_city

class LocationCommandTests(SimpleTestCase):
    def test_deprecated_command_only_prints_warning(self):
        output=StringIO()
        call_command("populate_locations",stdout=output)
        self.assertIn("sync_tipax_locations",output.getvalue())

    def test_normalize_persian_and_whitespace(self):
        self.assertEqual(normalize_location_name("  كرج  ي  "),"کرج ی")

    def test_parse_state(self):
        parsed=parse_tipax_state({"id":12,"title":"تهران"})
        self.assertEqual(parsed["state_id"],12)
        self.assertEqual(parsed["state_name"],"تهران")

    def test_parse_city(self):
        parsed=parse_tipax_city({"id":55,"stateId":12,"title":"تهران"})
        self.assertEqual(parsed["city_id"],55)
        self.assertEqual(parsed["state_id"],12)

    def test_invalid_payload_ignored(self):
        self.assertIsNone(parse_tipax_state({"title":"تهران"}))
        self.assertIsNone(parse_tipax_city({"id":1}))
