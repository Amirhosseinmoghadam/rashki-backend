from rest_framework import serializers

from addresses.models import (
    City,
    Province,
)

from shipping.models import (
    ShippingMethod,
    ShippingRateRule,
)


# =========================================================
# Method
# =========================================================


class ShippingMethodSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ShippingMethod

        fields = [
            "id",
            "code",
            "name",
            "provider",
            "service_code",
            "calculation_mode",
            "description",
            "estimated_min_days",
            "estimated_max_days",
            "is_active",
            "sort_order",
        ]

        read_only_fields = [
            "id",
        ]


# =========================================================
# Province
# =========================================================


class ShippingProvinceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Province

        fields = [
            "id",
            "name",
        ]

        read_only_fields = fields


# =========================================================
# City
# =========================================================


class ShippingCitySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = City

        fields = [
            "id",
            "name",
        ]

        read_only_fields = fields


# =========================================================
# Rate Rule
# =========================================================


class ShippingRateRuleSerializer(
    serializers.ModelSerializer
):

    method = (
        ShippingMethodSerializer(
            read_only=True
        )
    )

    method_id = (
        serializers.PrimaryKeyRelatedField(
            source="method",
            queryset=(
                ShippingMethod.objects.all()
            ),
            write_only=True,
        )
    )

    province = (
        ShippingProvinceSerializer(
            read_only=True
        )
    )

    province_id = (
        serializers.PrimaryKeyRelatedField(
            source="province",
            queryset=Province.objects.all(),
            required=False,
            allow_null=True,
            write_only=True,
        )
    )

    city = ShippingCitySerializer(
        read_only=True
    )

    city_id = (
        serializers.PrimaryKeyRelatedField(
            source="city",
            queryset=City.objects.all(),
            required=False,
            allow_null=True,
            write_only=True,
        )
    )

    class Meta:

        model = ShippingRateRule

        fields = [
            "id",
            "method",
            "method_id",
            "destination_scope",
            "province",
            "province_id",
            "city",
            "city_id",
            "min_weight_grams",
            "max_weight_grams",
            "base_price_toman",
            "included_weight_grams",
            "additional_per_kg_toman",
            "priority",
            "effective_from",
            "effective_to",
            "is_active",
            "note",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(
        self,
        attrs,
    ):

        instance = self.instance

        scope = attrs.get(
            "destination_scope",
            (
                instance.destination_scope
                if instance
                else
                ShippingRateRule
                .DestinationScope
                .NATIONWIDE
            ),
        )

        province = attrs.get(
            "province",
            (
                instance.province
                if instance
                else None
            ),
        )

        city = attrs.get(
            "city",
            (
                instance.city
                if instance
                else None
            ),
        )

        min_weight = attrs.get(
            "min_weight_grams",
            (
                instance.min_weight_grams
                if instance
                else 0
            ),
        )

        max_weight = attrs.get(
            "max_weight_grams",
            (
                instance.max_weight_grams
                if instance
                else None
            ),
        )

        effective_from = attrs.get(
            "effective_from",
            (
                instance.effective_from
                if instance
                else None
            ),
        )

        effective_to = attrs.get(
            "effective_to",
            (
                instance.effective_to
                if instance
                else None
            ),
        )

        if (
            max_weight is not None
            and max_weight < min_weight
        ):

            raise serializers.ValidationError(
                {
                    "max_weight_grams": (
                        "حداکثر وزن نمی‌تواند "
                        "کمتر از حداقل وزن باشد."
                    )
                }
            )

        if (
            effective_from
            and effective_to
            and effective_to
            <= effective_from
        ):

            raise serializers.ValidationError(
                {
                    "effective_to": (
                        "پایان اعتبار باید بعد "
                        "از شروع اعتبار باشد."
                    )
                }
            )

        if (
            scope
            == ShippingRateRule
            .DestinationScope
            .NATIONWIDE
        ):

            if province or city:

                raise serializers.ValidationError(
                    {
                        "destination_scope": (
                            "برای تعرفه کل کشور "
                            "استان و شهر نباید "
                            "مشخص شوند."
                        )
                    }
                )

        elif (
            scope
            == ShippingRateRule
            .DestinationScope
            .PROVINCE
        ):

            if not province:

                raise serializers.ValidationError(
                    {
                        "province_id": (
                            "انتخاب استان الزامی است."
                        )
                    }
                )

            if city:

                raise serializers.ValidationError(
                    {
                        "city_id": (
                            "برای تعرفه استانی "
                            "شهر نباید مشخص شود."
                        )
                    }
                )

        elif (
            scope
            == ShippingRateRule
            .DestinationScope
            .CITY
        ):

            if not city:

                raise serializers.ValidationError(
                    {
                        "city_id": (
                            "انتخاب شهر الزامی است."
                        )
                    }
                )

            if province:

                raise serializers.ValidationError(
                    {
                        "province_id": (
                            "برای تعرفه شهری "
                            "استان را انتخاب نکنید."
                        )
                    }
                )

        return attrs


# =========================================================
# Quote Request
# =========================================================


class ShippingQuoteRequestSerializer(
    serializers.Serializer
):

    # آدرس ذخیره‌شده متعلق به User.
    address_id = serializers.IntegerField(
        min_value=1,
    )


# =========================================================
# Quote
# =========================================================


class ShippingQuoteSerializer(
    serializers.Serializer
):

    method = ShippingMethodSerializer()

    amount_toman = serializers.IntegerField(
        allow_null=True
    )

    weight_grams = serializers.IntegerField()

    is_available = serializers.BooleanField()

    unavailable_reason = serializers.CharField(
        allow_null=True
    )

    provider_data = serializers.JSONField(
        allow_null=True,
        read_only=True,
    )