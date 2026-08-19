"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
# ---------------------------------------------------------
# Admin Site
# ---------------------------------------------------------

    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

# ---------------------------------------------------------
# sms
# ---------------------------------------------------------

# SMS API
    path(
        "api/sms/",include("utils.sms.api.urls"),
    ),


# ---------------------------------------------------------
# accounts
# ---------------------------------------------------------

    path(
        "api/v1/accounts/", include("accounts.api.v1.urls", namespace="accounts_api_v1")
    ),
# ---------------------------------------------------------
#Locations
# ---------------------------------------------------------

    path(
        "api/v1/locations/",include("addresses.api.v1.urls", namespace="addresses_api_v1"),
    ),
# ---------------------------------------------------------
#swagger
# ---------------------------------------------------------

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
