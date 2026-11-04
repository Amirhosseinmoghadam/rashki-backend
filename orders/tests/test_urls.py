from django.test import SimpleTestCase
from django.urls import resolve
from orders.api.v1.views import OrderListCreateAPIView, OrderDetailAPIView, OrderCancelAPIView


class OrderURLTests(SimpleTestCase):
    def test_list_path(self):
        from orders.api.v1.urls import urlpatterns
        self.assertEqual(urlpatterns[0].name, 'order-list-create')
        self.assertIs(urlpatterns[0].callback.view_class, OrderListCreateAPIView)

    def test_cancel_path(self):
        from orders.api.v1.urls import urlpatterns
        self.assertEqual(urlpatterns[1].name, 'order-cancel')
        self.assertIs(urlpatterns[1].callback.view_class, OrderCancelAPIView)

    def test_detail_path(self):
        from orders.api.v1.urls import urlpatterns
        self.assertEqual(urlpatterns[2].name, 'order-detail')
        self.assertIs(urlpatterns[2].callback.view_class, OrderDetailAPIView)
