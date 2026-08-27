from django.urls import path
from brands.api.v1.views import (
    BrandListView,
    BrandDetailView,
)

app_name = "brands"

urlpatterns = [
    # Brand URLs
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("brands/<str:identifier>/", BrandDetailView.as_view(), name="brand-detail"),
]
