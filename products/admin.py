from django.contrib import admin

from .models import Product, ProductVariant


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "slug",
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    search_fields = (
        "product__name",
        "sku",
    )