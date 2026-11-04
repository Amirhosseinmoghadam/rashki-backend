from wishlists.models import WishlistItem
from products.models import Product
from .base import WishlistBase

class WishlistAPITests(WishlistBase):
    def test_empty_list(self):
        res=self.authenticated().get(self.list_url)
        self.assertEqual(res.status_code,200)
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["data"]["total_objects"],0)
        self.assertEqual(res.data["data"]["results"], [])
    def test_list_contains_my_item(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        res=self.authenticated().get(self.list_url)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data["data"]["total_objects"],1)
        self.assertEqual(len(res.data["data"]["results"]), 1)
    def test_list_does_not_expose_other_user(self):
        WishlistItem.objects.create(user=self.other,product=self.product)
        res=self.authenticated().get(self.list_url)
        self.assertEqual(res.data["data"]["total_objects"],0)
        self.assertEqual(res.data["data"]["results"], [])
    def test_add_product_returns_201(self):
        res=self.authenticated().post(self.item_url())
        self.assertEqual(res.status_code,201)
        self.assertTrue(WishlistItem.objects.filter(user=self.user,product=self.product).exists())
    def test_add_is_idempotent(self):
        client=self.authenticated()
        self.assertEqual(client.post(self.item_url()).status_code,201)
        self.assertEqual(client.post(self.item_url()).status_code,200)
        self.assertEqual(WishlistItem.objects.filter(user=self.user,product=self.product).count(),1)
    def test_add_unknown_product_returns_404(self):
        self.assertEqual(self.authenticated().post('/api/v1/wishlist/999999999/').status_code,404)
    def test_add_draft_product_is_rejected(self):
        self.product.status=Product.Status.DRAFT;self.product.save(update_fields=["status"])
        self.assertEqual(self.authenticated().post(self.item_url()).status_code,404)
    def test_add_inactive_brand_is_rejected(self):
        self.brand.is_active=False;self.brand.save(update_fields=["is_active"])
        self.assertEqual(self.authenticated().post(self.item_url()).status_code,404)
    def test_add_inactive_category_is_rejected(self):
        self.category.is_active=False;self.category.save(update_fields=["is_active"])
        self.assertEqual(self.authenticated().post(self.item_url()).status_code,404)
    def test_remove_existing_item(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        res=self.authenticated().delete(self.item_url())
        self.assertEqual(res.status_code,200)
        self.assertFalse(WishlistItem.objects.filter(user=self.user,product=self.product).exists())
    def test_remove_nonexistent_returns_404(self):
        self.assertEqual(self.authenticated().delete(self.item_url()).status_code,404)
    def test_cannot_remove_another_users_item(self):
        WishlistItem.objects.create(user=self.other,product=self.product)
        self.assertEqual(self.authenticated().delete(self.item_url()).status_code,404)
        self.assertTrue(WishlistItem.objects.filter(user=self.other,product=self.product).exists())
    def test_ids_empty(self):
        res=self.authenticated().get(self.ids_url)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data["data"],[])
    def test_ids_only_current_user(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        WishlistItem.objects.create(user=self.other,product=self.product2)
        res=self.authenticated().get(self.ids_url)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data["data"],[self.product.pk])
    def test_ids_hide_draft(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.product.status=Product.Status.DRAFT;self.product.save(update_fields=["status"])
        self.assertEqual(self.authenticated().get(self.ids_url).data["data"],[])
