from django.db import IntegrityError, transaction
from django.utils import timezone
from wishlists.models import WishlistItem
from .base import WishlistBase

class WishlistModelTests(WishlistBase):
    def test_item_connects_user_and_product(self):
        obj=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertEqual(obj.user_id,self.user.pk)
        self.assertEqual(obj.product_id,self.product.pk)
    def test_created_at_is_populated(self):
        obj=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertLessEqual(obj.created_at,timezone.now())
    def test_duplicate_product_same_user_rejected_by_database(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        with self.assertRaises(IntegrityError):
            with transaction.atomic(): WishlistItem.objects.create(user=self.user,product=self.product)
    def test_same_product_can_belong_to_different_users(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        WishlistItem.objects.create(user=self.other,product=self.product)
        self.assertEqual(WishlistItem.objects.count(),2)
    def test_reverse_user_relation(self):
        obj=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertIn(obj,self.user.wishlist_items.all())
    def test_reverse_product_relation(self):
        obj=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertIn(obj,self.product.wishlist_items.all())
    def test_str_contains_user_and_product(self):
        obj=WishlistItem.objects.create(user=self.user,product=self.product)
        self.assertIn(str(self.product),str(obj))
    def test_user_deletion_cascades_to_wishlist(self):
        WishlistItem.objects.create(user=self.other,product=self.product)
        self.other.delete()
        self.assertFalse(WishlistItem.objects.exists())
    def test_product_deletion_cascades_to_wishlist(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.product.delete()
        self.assertFalse(WishlistItem.objects.exists())
