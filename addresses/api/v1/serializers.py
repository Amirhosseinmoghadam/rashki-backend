from rest_framework import serializers

from addresses.models import Address, City, Province
from addresses.services import (
    AddressServiceError,
    create_address,
    update_address,
)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ["id", "name"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]


class AddressSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(
        source="province.name",
        read_only=True,
    )

    city_name = serializers.CharField(
        source="city.name",
        read_only=True,
    )

    class Meta:
        model = Address
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
            "province",
            "province_name",
            "city",
            "city_name",
            "postal_code",
            "postal_address",
            "is_default",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "province_name",
            "city_name",
            "created_at",
            "updated_at",
        ]


class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "first_name",
            "last_name",
            "mobile_number",
            "phone_number",
            "province",
            "city",
            "postal_code",
            "postal_address",
            "is_default",
        ]

        extra_kwargs = {
            "first_name": {
                "required": True,
                "allow_null": False,
                "allow_blank": False,
            },
            "last_name": {
                "required": True,
                "allow_null": False,
                "allow_blank": False,
            },
            "mobile_number": {
                "required": True,
                "allow_null": False,
                "allow_blank": False,
            },
            "postal_code": {
                "required": True,
                "allow_null": False,
                "allow_blank": False,
            },
            "postal_address": {
                "required": True,
                "allow_null": False,
                "allow_blank": False,
            },
            "phone_number": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "is_default": {
                "required": False,
            },
        }

    def validate(self, attrs):
        instance = self.instance

        province = attrs.get(
            "province",
            getattr(
                instance,
                "province",
                None,
            ),
        )

        city = attrs.get(
            "city",
            getattr(
                instance,
                "city",
                None,
            ),
        )

        if (
            province is not None
            and city is not None
            and city.province_id != province.id
        ):
            raise serializers.ValidationError(
                {
                    "city": (
                        "شهر انتخاب‌شده متعلق به "
                        "استان انتخاب‌شده نیست."
                    )
                }
            )

        return attrs


class AddressCreateSerializer(AddressWriteSerializer):
    def create(self, validated_data):
        return create_address(
            user=self.context["request"].user,
            validated_data=validated_data,
        )


class AddressUpdateSerializer(AddressWriteSerializer):
    def update(self, instance, validated_data):
        try:
            return update_address(
                address=instance,
                validated_data=validated_data,
            )
        except AddressServiceError as exc:
            raise serializers.ValidationError(
                {
                    "is_default": str(exc),
                }
            ) from exc
