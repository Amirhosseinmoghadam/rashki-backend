from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    ProductViewSet,
    ProductImageViewSet,
    ProductAttributeViewSet,
)


app_name = "products_api_v1"


router = DefaultRouter()


router.register(
    r"products",
    ProductViewSet,
    basename="product",
)


router.register(
    r"product-images",
    ProductImageViewSet,
    basename="product-image",
)


router.register(
    r"product-attributes",
    ProductAttributeViewSet,
    basename="product-attribute",
)


urlpatterns = router.urls