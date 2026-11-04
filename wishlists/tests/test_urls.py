from django.test import SimpleTestCase
from django.urls import reverse,resolve
from wishlists.api.v1.views import WishlistListAPIView,WishlistItemAPIView,WishlistProductIdsAPIView

class WishlistURLTests(SimpleTestCase):
    def test_list_url(self):
        url=reverse("wishlists_api_v1:wishlist-list")
        self.assertEqual(url,"/api/v1/wishlist/")
        self.assertIs(resolve(url).func.view_class,WishlistListAPIView)
    def test_ids_url(self):
        url=reverse("wishlists_api_v1:wishlist-product-ids")
        self.assertEqual(url,"/api/v1/wishlist/product-ids/")
        self.assertIs(resolve(url).func.view_class,WishlistProductIdsAPIView)
    def test_item_url(self):
        url=reverse("wishlists_api_v1:wishlist-item",kwargs={"product_id":12})
        self.assertEqual(url,"/api/v1/wishlist/12/")
        self.assertIs(resolve(url).func.view_class,WishlistItemAPIView)
