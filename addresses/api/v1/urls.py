from django.urls import path

from addresses.api.v1.views import (
    AddressDetailAPIView,
    AddressListCreateAPIView,
    AddressSetDefaultAPIView,
    CityListView,
    ProvinceListView,
)

app_name = "addresses_api_v1"

urlpatterns = [
    path(
        "provinces/",
        ProvinceListView.as_view(),
        name="province-list",
    ),
    path(
        "provinces/<int:province_id>/cities/",
        CityListView.as_view(),
        name="city-list-by-province",
    ),
    path(
        "addresses/",
        AddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),
    path(
        "addresses/<int:pk>/",
        AddressDetailAPIView.as_view(),
        name="address-detail",
    ),
    path(
        "addresses/<int:pk>/set-default/",
        AddressSetDefaultAPIView.as_view(),
        name="address-set-default",
    ),
]
