from django.urls import path

from .views import (
    ContactRequestCreateAPIView,
    ContactRequestDetailAPIView,
    ContactRequestListAPIView,
)

app_name = "contact_api_v1"
urlpatterns = [
    # Public
    path(
        "",
        ContactRequestCreateAPIView.as_view(),
        name="contact-create",
    ),

    # Admin
    path(
        "admin/",
        ContactRequestListAPIView.as_view(),
        name="contact-admin-list",
    ),

    path(
        "admin/<int:pk>/",
        ContactRequestDetailAPIView.as_view(),
        name="contact-admin-detail",
    ),
]