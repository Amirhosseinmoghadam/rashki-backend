from django.urls import path

from .views import (
    # Product
    ProductListCreateAPIView,
    ProductRetrieveUpdateDestroyAPIView,
    # Product Image
    ProductImageListCreateAPIView,
    ProductImageRetrieveUpdateDestroyAPIView,
    # Attribute Group
    AttributeGroupListCreateAPIView,
    AttributeGroupRetrieveUpdateDestroyAPIView,
    # Attribute
    AttributeListCreateAPIView,
    AttributeRetrieveUpdateDestroyAPIView,
    # Attribute Value
    AttributeValueListCreateAPIView,
    AttributeValueRetrieveUpdateDestroyAPIView,
    # Product Variant
    ProductVariantListCreateAPIView,
    ProductVariantRetrieveUpdateDestroyAPIView,
    # Product Motorcycle Compatibility
    ProductMotorcycleCompatibilityListCreateAPIView,
    ProductMotorcycleCompatibilityRetrieveUpdateDestroyAPIView,
)

app_name = "products"

urlpatterns = [
    # =========================================================
    # Product URLs
    # =========================================================
    path(
        "products/",
        ProductListCreateAPIView.as_view(),
        name="product-list-create",
    ),
    path(
        "products/<slug:slug>/",
        ProductRetrieveUpdateDestroyAPIView.as_view(),
        name="product-retrieve-update-destroy",
    ),
    # =========================================================
    # Product Image URLs
    # =========================================================
    path(
        "products/<int:product_id>/images/",
        ProductImageListCreateAPIView.as_view(),
        name="product-image-list-create",
    ),
    path(
        "products/images/<int:pk>/",
        ProductImageRetrieveUpdateDestroyAPIView.as_view(),
        name="product-image-retrieve-update-destroy",
    ),
    # =========================================================
    # Attribute Group URLs
    # =========================================================
    path(
        "attribute-groups/",
        AttributeGroupListCreateAPIView.as_view(),
        name="attribute-group-list-create",
    ),
    path(
        "attribute-groups/<int:pk>/",
        AttributeGroupRetrieveUpdateDestroyAPIView.as_view(),
        name="attribute-group-retrieve-update-destroy",
    ),
    # =========================================================
    # Attribute URLs
    # =========================================================
    path(
        "attributes/",
        AttributeListCreateAPIView.as_view(),
        name="attribute-list-create",
    ),
    path(
        "attributes/<int:pk>/",
        AttributeRetrieveUpdateDestroyAPIView.as_view(),
        name="attribute-retrieve-update-destroy",
    ),
    # =========================================================
    # Attribute Value URLs
    # =========================================================
    path(
        "attribute-values/",
        AttributeValueListCreateAPIView.as_view(),
        name="attribute-value-list-create",
    ),
    path(
        "attribute-values/<int:pk>/",
        AttributeValueRetrieveUpdateDestroyAPIView.as_view(),
        name="attribute-value-retrieve-update-destroy",
    ),
    # =========================================================
    # Product Variant URLs
    # =========================================================
    path(
        "products/<int:product_id>/variants/",
        ProductVariantListCreateAPIView.as_view(),
        name="product-variant-list-create",
    ),
    path(
        "products/variants/<int:pk>/",
        ProductVariantRetrieveUpdateDestroyAPIView.as_view(),
        name="product-variant-retrieve-update-destroy",
    ),
    # =========================================================
    # Product Motorcycle Compatibility URLs
    # =========================================================
    path(
        "products/<int:product_id>/motorcycle-compatibilities/",
        ProductMotorcycleCompatibilityListCreateAPIView.as_view(),
        name="product-motorcycle-compatibility-list-create",
    ),
    path(
        "products/motorcycle-compatibilities/<int:pk>/",
        ProductMotorcycleCompatibilityRetrieveUpdateDestroyAPIView.as_view(),
        name="product-motorcycle-compatibility-retrieve-update-destroy",
    ),
]
