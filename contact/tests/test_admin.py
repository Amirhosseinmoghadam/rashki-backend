from django.contrib import admin
from django.test import TestCase,RequestFactory
from contact.admin import ContactRequestAdmin
from contact.models import ContactRequest
from .base import make_request


class ContactAdminTests(TestCase):
    def test_registered_and_read_only(self):
        self.assertIn(ContactRequest,admin.site._registry)
        model_admin=admin.site._registry[ContactRequest]
        self.assertIn("is_read",model_admin.list_editable)
        self.assertIn("phone_number",model_admin.readonly_fields)

    def test_manual_creation_disabled(self):
        model_admin=admin.site._registry[ContactRequest]
        self.assertFalse(model_admin.has_add_permission(RequestFactory().get("/admin/")))

    def test_mark_read_and_unread(self):
        obj=make_request()
        instance=ContactRequestAdmin(ContactRequest,admin.site)
        qs=ContactRequest.objects.filter(pk=obj.pk)
        instance.mark_as_read(None,qs)
        obj.refresh_from_db();self.assertTrue(obj.is_read)
        instance.mark_as_unread(None,qs)
        obj.refresh_from_db();self.assertFalse(obj.is_read)
