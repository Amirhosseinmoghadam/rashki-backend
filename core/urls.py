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
from django.conf import settings
from django.conf.urls.static import static


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
        "api/sms/",
        include("utils.sms.api.urls"),
    ),
    # ---------------------------------------------------------
    # accounts
    # ---------------------------------------------------------
    path(
        "api/v1/accounts/", include("accounts.api.v1.urls", namespace="accounts_api_v1")
    ),
    # ---------------------------------------------------------
    # addresses
    # ---------------------------------------------------------
    path(
        "api/v1/locations/",
        include("addresses.api.v1.urls", namespace="addresses_api_v1"),
    ),
    # ---------------------------------------------------------
    # articles
    # ---------------------------------------------------------
    path(
        "api/v1/articles/",
        include("articles.api.v1.urls", namespace="articles_api_v1"),
    ),
    # ---------------------------------------------------------
    # brands
    # ---------------------------------------------------------
    path(
        "api/v1/brands/",
        include("brands.api.v1.urls", namespace="brands_api_v1"),
    ),
    # ---------------------------------------------------------
    # contact
    # ---------------------------------------------------------
    path(
        "api/v1/contact/",
        include("contact.api.v1.urls", namespace="contact_api_v1"),
    ),
    # ---------------------------------------------------------
    # carts
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include(
            "carts.api.v1.urls",
            namespace="carts_api_v1",
        ),
    ),
    # ---------------------------------------------------------
    # categories
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include("categories.api.v1.urls"),
    ),
    # ---------------------------------------------------------
    # discounts
    # ---------------------------------------------------------
    path(
    "api/v1/",
    include(
        "discounts.api.v1.urls",
        namespace="discounts_api_v1",
    ),
),
    # ---------------------------------------------------------
    # products
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include("products.api.v1.urls"),
    ),
    # ---------------------------------------------------------
    # shipping
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include(
            "shipping.api.v1.urls",
            namespace="shipping_api_v1",
        ),
    ),
    # ---------------------------------------------------------
    # payments
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include(
            "payments.api.v1.urls",
            namespace="payments_api_v1",
        ),
    ),
    # ---------------------------------------------------------
    # motorcycles
    # ---------------------------------------------------------

    path(
        "api/v1/motorcycles/",
        include("motorcycles.api.v1.urls"),
    ),
    # ---------------------------------------------------------
    # wishlists
    # ---------------------------------------------------------
    path(
    "api/v1/",
    include(
        "wishlists.api.v1.urls",
        namespace="wishlists_api_v1",
    ),
    ),
    # ---------------------------------------------------------
    # orders
    # ---------------------------------------------------------
    path(
        "api/v1/",
        include(
            "orders.api.v1.urls"
        ),
    ),
    # ---------------------------------------------------------
    # swagger
    # ---------------------------------------------------------
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )