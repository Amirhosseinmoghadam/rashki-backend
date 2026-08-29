from rest_framework.routers import DefaultRouter

from categories.api.v1.views import CategoryViewSet

router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

urlpatterns = router.urls
