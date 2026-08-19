from rest_framework import serializers
from addresses.models import Province, City, Address
from django.db import transaction

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


class AddressCreateSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        province = attrs.get("province")
        city = attrs.get("city")

        if province and city:
            if city.province_id != province.id:
                raise serializers.ValidationError(
                    {
                        "city": (
                            "شهر انتخاب‌شده متعلق به "
                            "استان انتخاب‌شده نیست."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        addresses = (
            Address.objects
            .select_for_update()
            .filter(user=user)
        )

        has_addresses = addresses.exists()

        # اولین آدرس کاربر پیش‌فرض باشد
        if not has_addresses:
            validated_data["is_default"] = True

        if validated_data.get("is_default") is True:
            addresses.filter(
                is_default=True
            ).update(
                is_default=False
            )

        return Address.objects.create(
            user=user,
            **validated_data,
        )


class AddressUpdateSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        instance = self.instance

        province = attrs.get(
            "province",
            instance.province,
        )

        city = attrs.get(
            "city",
            instance.city,
        )

        if province and city:
            if city.province_id != province.id:
                raise serializers.ValidationError(
                    {
                        "city": (
                            "شهر انتخاب‌شده متعلق به "
                            "استان انتخاب‌شده نیست."
                        )
                    }
                )

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance.user

        # آدرس پیش‌فرض دیگری انتخاب شده
        if validated_data.get("is_default") is True:
            (
                Address.objects
                .select_for_update()
                .filter(
                    user=user,
                    is_default=True,
                )
                .exclude(
                    pk=instance.pk
                )
                .update(
                    is_default=False
                )
            )

        # اجازه نمی‌دهیم کاربر تنها آدرس پیش‌فرض
        # خودش را unset کند.
        if (
            validated_data.get("is_default") is False
            and instance.is_default
        ):
            raise serializers.ValidationError(
                {
                    "is_default": (
                        "نمی‌توانید آدرس پیش‌فرض را "
                        "بدون انتخاب آدرس جدید حذف کنید."
                    )
                }
            )

        return super().update(
            instance,
            validated_data,
        )