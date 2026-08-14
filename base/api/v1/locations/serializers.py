from rest_framework import serializers
from base.models import Province, City


class ProvinceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Province model.
    Outputs only the 'id' and 'name' fields.
    """

    class Meta:
        model = Province
        fields = ["id", "name"]


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for the City model.
    Outputs only the 'id' and 'name' fields.
    The relationship to the province is handled via URL filtering in the view.
    """

    class Meta:
        model = City
        fields = ["id", "name"]
