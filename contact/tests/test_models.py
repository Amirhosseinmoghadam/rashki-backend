from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from contact.models import ContactRequest
from .base import make_request


class ContactModelTests(TestCase):
    def test_defaults_and_timestamps(self):
        item = make_request()
        self.assertFalse(item.is_read)
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)

    def test_string_representation(self):
        item = make_request()
        self.assertIn("علی احمدی", str(item))
        self.assertIn(item.get_subject_display(), str(item))

    def test_valid_mobile_passes_full_clean(self):
        make_request().full_clean()

    def test_invalid_mobile_fails_full_clean(self):
        item = make_request(phone_number="12345678901")
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_subject_choices(self):
        self.assertEqual(len(ContactRequest.Subject.choices), 5)
        item = make_request(subject="unknown")
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_default_ordering_newest_first(self):
        old = make_request(phone_number="09111111111")
        new = make_request(phone_number="09222222222")
        ContactRequest.objects.filter(pk=old.pk).update(created_at=timezone.now()-timezone.timedelta(days=1))
        self.assertEqual(list(ContactRequest.objects.values_list("pk",flat=True))[:2], [new.pk,old.pk])

    def test_description_length_is_metadata_on_textfield(self):
        # Django TextField.max_length does not add a model-level MaxLengthValidator.
        field = ContactRequest._meta.get_field("description")
        self.assertEqual(field.max_length, 3000)
        item = make_request(description="x" * 3001)
        item.full_clean()  # Current model behavior; API serializer validates length.
