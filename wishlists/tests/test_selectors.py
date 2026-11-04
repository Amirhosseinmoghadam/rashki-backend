from wishlists.models import WishlistItem
from wishlists.selectors import get_public_category_ids, get_public_products_queryset, get_user_wishlist_queryset
from categories.models import Category
from products.models import Product
from .base import WishlistBase

class WishlistSelectorTests(WishlistBase):
    def test_active_root_category_is_public(self):
        self.assertIn(self.category.pk,get_public_category_ids())
    def test_inactive_root_category_is_private(self):
        self.category.is_active=False;self.category.save(update_fields=["is_active"])
        self.assertNotIn(self.category.pk,get_public_category_ids())
    def test_child_of_inactive_parent_is_private(self):
        child=Category.objects.create(name="Child category",parent=self.category,is_active=True)
        self.category.is_active=False;self.category.save(update_fields=["is_active"])
        self.assertNotIn(child.pk,get_public_category_ids())
    def test_public_products_include_active(self):
        self.assertIn(self.product,get_public_products_queryset())
    def test_draft_product_is_not_public(self):
        self.product.status=Product.Status.DRAFT;self.product.save(update_fields=["status"])
        self.assertNotIn(self.product,get_public_products_queryset())
    def test_archived_product_is_not_public(self):
        self.product.status=Product.Status.ARCHIVED;self.product.save(update_fields=["status"])
        self.assertNotIn(self.product,get_public_products_queryset())
    def test_inactive_brand_hides_product(self):
        self.brand.is_active=False;self.brand.save(update_fields=["is_active"])
        self.assertNotIn(self.product,get_public_products_queryset())
    def test_inactive_category_hides_product(self):
        self.category.is_active=False;self.category.save(update_fields=["is_active"])
        self.assertNotIn(self.product,get_public_products_queryset())
    def test_public_product_can_have_no_brand(self):
        self.product.brand=None;self.product.save(update_fields=["brand"])
        self.assertIn(self.product,get_public_products_queryset())
    def test_selector_is_scoped_to_user(self):
        mine=WishlistItem.objects.create(user=self.user,product=self.product)
        WishlistItem.objects.create(user=self.other,product=self.product2)
        self.assertEqual(list(get_user_wishlist_queryset(self.user)),[mine])
    def test_selector_hides_draft_saved_item(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.product.status=Product.Status.DRAFT;self.product.save(update_fields=["status"])
        self.assertFalse(get_user_wishlist_queryset(self.user).exists())
    def test_selector_hides_inactive_brand_item(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.brand.is_active=False;self.brand.save(update_fields=["is_active"])
        self.assertFalse(get_user_wishlist_queryset(self.user).exists())
    def test_selector_hides_inactive_parent_category(self):
        child=Category.objects.create(name="Wishlist child",parent=self.category,is_active=True)
        self.product.category=child;self.product.save(update_fields=["category"])
        WishlistItem.objects.create(user=self.user,product=self.product)
        self.category.is_active=False;self.category.save(update_fields=["is_active"])
        self.assertFalse(get_user_wishlist_queryset(self.user).exists())
    def test_selector_selects_product_relationship(self):
        WishlistItem.objects.create(user=self.user,product=self.product)
        item=get_user_wishlist_queryset(self.user).get()
        self.assertIn("product",item._state.fields_cache)
