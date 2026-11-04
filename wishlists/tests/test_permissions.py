from rest_framework.test import APIClient
from wishlists.models import WishlistItem
from .base import WishlistBase

class WishlistPermissionsTests(WishlistBase):
    def test_guest_cannot_list(self):
        self.assertIn(APIClient().get(self.list_url).status_code,(401,403))
    def test_guest_cannot_get_ids(self):
        self.assertIn(APIClient().get(self.ids_url).status_code,(401,403))
    def test_guest_cannot_add(self):
        self.assertIn(APIClient().post(self.item_url()).status_code,(401,403))
        self.assertFalse(WishlistItem.objects.exists())
    def test_guest_cannot_remove(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertIn(APIClient().delete(self.item_url()).status_code,(401,403))
        self.assertTrue(WishlistItem.objects.exists())
    def test_different_user_cannot_view_saved_item(self):
        WishlistItem.objects.create(user=self.other,product=self.product)
        self.assertEqual(self.authenticated().get(self.list_url).data["data"]["total_objects"],0)
    def test_two_users_can_save_same_product(self):
        self.assertEqual(self.authenticated().post(self.item_url()).status_code,201)
        self.assertEqual(self.authenticated(self.other).post(self.item_url()).status_code,201)
        self.assertEqual(WishlistItem.objects.count(),2)
