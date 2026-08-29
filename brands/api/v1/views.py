from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from brands.models import Brand

from .serializers import (
    BrandSerializer,
    BrandListSerializer,
    BrandCreateUpdateSerializer,
)

from brands.api.v1.openapi.schema import (
    brand_list_schema,
    brand_create_schema,
    brand_detail_schema,
    brand_update_schema,
    brand_delete_schema,
)


class BrandListView(APIView):
    """
    List all brands or create a new brand.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @brand_list_schema
    def get(self, request):
        brands = Brand.objects.filter(is_active=True)

        serializer = BrandListSerializer(
            brands,
            many=True,
        )

        return Response(serializer.data)

    @brand_create_schema
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": ("You do not have permission " "to create brands.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BrandCreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class BrandDetailView(APIView):
    """
    Retrieve, update or delete a brand.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @brand_detail_schema
    def get(self, request, identifier):
        brand = self._get_brand(identifier)

        serializer = BrandSerializer(brand)

        return Response(serializer.data)

    @brand_update_schema
    def put(self, request, identifier):
        if not request.user.is_staff:
            return Response(
                {"detail": ("You do not have permission " "to update brands.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        brand = self._get_brand(identifier)

        serializer = BrandCreateUpdateSerializer(
            brand,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    @brand_delete_schema
    def delete(self, request, identifier):
        if not request.user.is_staff:
            return Response(
                {"detail": ("You do not have permission " "to delete brands.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        brand = self._get_brand(identifier)

        brand.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @staticmethod
    def _get_brand(identifier):
        try:
            return Brand.objects.get(pk=identifier)

        except (Brand.DoesNotExist, ValueError):
            return get_object_or_404(
                Brand,
                slug=identifier,
            )
