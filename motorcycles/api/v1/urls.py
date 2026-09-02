from rest_framework.routers import (
    DefaultRouter,
)

from motorcycles.api.v1.views import (
    MotorcycleBrandViewSet,
    MotorcycleModelViewSet,
)


app_name = "motorcycles_api_v1"


router = DefaultRouter()


router.register(
    r"motorcycle-brands",
    MotorcycleBrandViewSet,
    basename="motorcycle-brand",
)


router.register(
    r"motorcycles",
    MotorcycleModelViewSet,
    basename="motorcycle",
)


urlpatterns = router.urls