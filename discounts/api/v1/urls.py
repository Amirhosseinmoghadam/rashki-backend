from django.urls import path

from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    DiscountCodeViewSet,
    DiscountValidateAPIView,
)


app_name = "discounts_api_v1"


router = DefaultRouter()


# Admin CRUD
router.register(
    r"discount-codes",
    DiscountCodeViewSet,
    basename="discount-code",
)


urlpatterns = [

    # User validates a discount code.
    path(
        "discounts/validate/",
        DiscountValidateAPIView.as_view(),
        name="discount-validate",
    ),

]


urlpatterns += router.urls