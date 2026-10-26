from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from contact.api.v1.serializers import (ContactRequestCreateSerializer, ContactRequestAdminSerializer, ContactRequestStatusSerializer)
from .base import payload, make_request


class CreateSerializerTests(TestCase):
    def test_valid(self):
        serializer=ContactRequestCreateSerializer(data=payload())
        self.assertTrue(serializer.is_valid(),serializer.errors)

    def test_persian_digits_are_normalized(self):
        serializer=ContactRequestCreateSerializer(data=payload(phone_number="۰۹۱۲۳۴۵۶۷۸۹"))
        self.assertTrue(serializer.is_valid(),serializer.errors)
        self.assertEqual(serializer.validated_data["phone_number"],"09123456789")

    def test_invalid_phone(self):
        for phone in ["08123456789","0912345","abcdefghijk"]:
            with self.subTest(phone=phone):
                serializer=ContactRequestCreateSerializer(data=payload(phone_number=phone))
                self.assertFalse(serializer.is_valid())
                self.assertIn("phone_number",serializer.errors)

    def test_missing_required_fields(self):
        for field in payload():
            with self.subTest(field=field):
                data=payload();data.pop(field)
                serializer=ContactRequestCreateSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field,serializer.errors)

    def test_short_names(self):
        for field in ("first_name","last_name"):
            with self.subTest(field=field):
                serializer=ContactRequestCreateSerializer(data=payload(**{field:"ا"}))
                self.assertFalse(serializer.is_valid())
                self.assertIn(field,serializer.errors)

    def test_invalid_subject(self):
        serializer=ContactRequestCreateSerializer(data=payload(subject="invalid"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("subject",serializer.errors)

    def test_short_or_blank_description(self):
        for text in ("    ","abc"):
            with self.subTest(text=text):
                serializer=ContactRequestCreateSerializer(data=payload(description=text))
                self.assertFalse(serializer.is_valid())
                self.assertIn("description",serializer.errors)

    def test_description_over_3000_chars_is_rejected(self):
        serializer = ContactRequestCreateSerializer(data=payload(description="x" * 3001))
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_duplicate_within_five_minutes_is_rejected(self):
        make_request()
        serializer=ContactRequestCreateSerializer(data=payload())
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors",serializer.errors)

    def test_old_identical_request_is_accepted(self):
        item=make_request()
        type(item).objects.filter(pk=item.pk).update(created_at=timezone.now()-timedelta(minutes=6))
        serializer=ContactRequestCreateSerializer(data=payload())
        self.assertTrue(serializer.is_valid(),serializer.errors)

    def test_different_description_is_accepted(self):
        make_request()
        serializer=ContactRequestCreateSerializer(data=payload(description="توضیحات جدید و متفاوت"))
        self.assertTrue(serializer.is_valid(),serializer.errors)

    def test_create_serializer_excludes_internal_status(self):
        serializer=ContactRequestCreateSerializer(data=payload(is_read=True))
        self.assertTrue(serializer.is_valid(),serializer.errors)
        self.assertNotIn("is_read",serializer.validated_data)


class AdminSerializersTests(TestCase):
    def test_admin_data_contains_status_and_display(self):
        item=make_request()
        data=ContactRequestAdminSerializer(item).data
        self.assertFalse(data["is_read"])
        self.assertEqual(data["subject_display"],item.get_subject_display())

    def test_status_serializer_allows_boolean(self):
        serializer=ContactRequestStatusSerializer(data={"is_read":True})
        self.assertTrue(serializer.is_valid(),serializer.errors)

    def test_status_serializer_cannot_change_description(self):
        serializer=ContactRequestStatusSerializer(data={"is_read":True,"description":"changed"})
        self.assertTrue(serializer.is_valid(),serializer.errors)
        self.assertNotIn("description",serializer.validated_data)
