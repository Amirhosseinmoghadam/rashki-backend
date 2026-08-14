from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from base.models import Province, City
from .serializers import ProvinceSerializer, CitySerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Locations"])
class ProvinceListView(ListAPIView):
    """
    API View to provide a list of all Provinces.
    Returns 'id' and 'name' for each province.
    Accessible by any user (AllowAny).
    """

    queryset = Province.objects.all().order_by("name")
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]
    pagination_class = None


@extend_schema(tags=["Locations"])
class CityListView(ListAPIView):
    """
    API View to provide a list of Cities filtered by a specific Province ID.
    The Province ID is expected as part of the URL (e.g., /provinces/<province_id>/cities/).
    Returns 'id' and 'name' for each city within that province.
    Accessible by any user (AllowAny).
    """

    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        """
        Overrides the default queryset behavior to filter cities
        based on the 'province_id' captured from the URL.
        """
        province_id = self.kwargs.get("province_id")
        if province_id is not None:
            return City.objects.filter(province_id=province_id).order_by("name")
        return City.objects.none()
