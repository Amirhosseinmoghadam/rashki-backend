from django.urls import path

from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    ShippingMethodViewSet,
    ShippingQuoteAPIView,
    ShippingRateRuleViewSet,
)


app_name = "shipping_api_v1"


router = DefaultRouter()


router.register(
    r"shipping-methods",
    ShippingMethodViewSet,
    basename="shipping-method",
)


router.register(
    r"shipping-rate-rules",
    ShippingRateRuleViewSet,
    basename="shipping-rate-rule",
)


urlpatterns = [

    path(
        "shipping/quotes/",
        ShippingQuoteAPIView.as_view(),
        name="shipping-quotes",
    ),

]


urlpatterns += router.urls