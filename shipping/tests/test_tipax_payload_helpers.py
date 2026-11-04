from django.test import SimpleTestCase
from shipping.tipax_packing import _extract_items, _decimal, _to_ascii_digits, TipaxPackingSyncError


class TipaxPayloadHelperTests(SimpleTestCase):
    def test_accept_list(self):
        self.assertEqual(_extract_items([{"id": 1}], label="packings"), [{"id": 1}])

    def test_accept_dict_result(self):
        self.assertEqual(_extract_items({"result": [{"id": 1}], "totalCount": 1}, label="packings"), [{"id": 1}])

    def test_reject_wrong_total_count(self):
        with self.assertRaises(TipaxPackingSyncError):
            _extract_items({"result": [], "totalCount": 2}, label="packings")

    def test_reject_missing_result(self):
        with self.assertRaises(TipaxPackingSyncError):
            _extract_items({"data": []}, label="packings")

    def test_reject_invalid_count(self):
        with self.assertRaises(TipaxPackingSyncError):
            _extract_items({"result": [], "totalCount": "bad"}, label="packings")

    def test_persian_digits_normalized(self):
        self.assertEqual(_to_ascii_digits("۱۲۳٤٥"), "12345")

    def test_invalid_numeric_value(self):
        with self.assertRaises(TipaxPackingSyncError):
            _decimal("invalid")

    def test_empty_numeric_value_is_none(self):
        self.assertIsNone(_decimal(""))
