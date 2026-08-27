from rest_framework import serializers
from brands.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""

    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'slug',
            'logo',
            'description',
            'website',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class BrandListSerializer(serializers.ModelSerializer):
    """Serializer for Brand list view"""

    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'slug',
            'logo',
            'description',
            'is_active',
        ]


class BrandCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Brand create and update operations"""

    class Meta:
        model = Brand
        fields = [
            'name',
            'slug',
            'logo',
            'description',
            'website',
            'is_active',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']