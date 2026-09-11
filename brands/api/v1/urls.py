from rest_framework.routers import DefaultRouter

from brands.api.v1.views import BrandViewSet


app_name = "brands_api_v1"


router = DefaultRouter()

router.register(
    r"brands",
    BrandViewSet,
    basename="brand",
)


urlpatterns = router.urls