from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .serializers import (
    BrandSerializer,
    BrandListSerializer,
    BrandCreateUpdateSerializer,
)
from brands.models import Brand
from brands.api.v1.openapi.responses import (
    brand_list_response,
    brand_detail_response,
    brand_create_response,
    common_error_response,
    validation_error_response,
)
from drf_spectacular.utils import extend_schema


class BrandListView(APIView):
    """
    List all brands or create a new brand.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List Brands",
        description="Get a list of all active brands",
        responses={
            200: brand_list_response,
        },
        tags=["Brands"],
    )
    def get(self, request):
        brands = Brand.objects.filter(is_active=True)
        serializer = BrandListSerializer(brands, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Brand",
        description="Create a new brand (requires staff permissions)",
        request=BrandCreateUpdateSerializer,
        responses={
            201: brand_create_response,
            400: validation_error_response,
            401: common_error_response,
            403: common_error_response,
        },
        tags=["Brands"],
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to create brands."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BrandCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BrandDetailView(APIView):
    """
    Retrieve, update or delete a brand.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get Brand",
        description="Get details of a specific brand by ID or slug",
        responses={
            200: brand_detail_response,
            404: common_error_response,
        },
        tags=["Brands"],
    )
    def get(self, request, identifier):
        # Try to get by ID first, then by slug
        try:
            brand = Brand.objects.get(pk=identifier)
        except (Brand.DoesNotExist, ValueError):
            brand = get_object_or_404(Brand, slug=identifier)

        serializer = BrandSerializer(brand)
        return Response(serializer.data)

    @extend_schema(
        summary="Update Brand",
        description="Update an existing brand (requires staff permissions)",
        request=BrandCreateUpdateSerializer,
        responses={
            200: brand_detail_response,
            400: validation_error_response,
            404: common_error_response,
        },
        tags=["Brands"],
    )
    def put(self, request, identifier):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to update brands."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            brand = Brand.objects.get(pk=identifier)
        except (Brand.DoesNotExist, ValueError):
            brand = get_object_or_404(Brand, slug=identifier)

        serializer = BrandCreateUpdateSerializer(brand, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete Brand",
        description="Delete a brand (requires staff permissions)",
        responses={
            204: None,
            404: common_error_response,
        },
        tags=["Brands"],
    )
    def delete(self, request, identifier):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete brands."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            brand = Brand.objects.get(pk=identifier)
        except (Brand.DoesNotExist, ValueError):
            brand = get_object_or_404(Brand, slug=identifier)

        brand.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
