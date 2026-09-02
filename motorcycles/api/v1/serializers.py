from rest_framework import serializers

from motorcycles.models import (
    MotorcycleBrand,
    MotorcycleModel,
)

from utils.normalizers import (
    normalize_single_line_text,
)


# =========================================================
# Motorcycle Brand Reference
# =========================================================


class MotorcycleBrandReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = MotorcycleBrand

        fields = [
            "id",
            "name",
            "slug",
        ]

        read_only_fields = fields


# =========================================================
# Motorcycle Brand List
# =========================================================


class MotorcycleBrandListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = MotorcycleBrand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
        ]

        read_only_fields = fields


# =========================================================
# Motorcycle Brand Detail
# =========================================================


class MotorcycleBrandDetailSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = MotorcycleBrand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# =========================================================
# Motorcycle Brand Create / Update
# =========================================================


class MotorcycleBrandCreateUpdateSerializer(
    serializers.ModelSerializer
):

    name = serializers.CharField(
        max_length=150,
        required=True,
    )

    slug = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = MotorcycleBrand

        fields = [
            "name",
            "slug",
            "logo",
            "is_active",
        ]

        read_only_fields = [
            "slug",
        ]

    def validate_name(
        self,
        value,
    ):

        value = (
            normalize_single_line_text(
                value
            )
        )

        if not value:

            raise serializers.ValidationError(
                "نام برند موتورسیکلت "
                "الزامی است."
            )

        queryset = (
            MotorcycleBrand.objects.filter(
                name__iexact=value
            )
        )

        if self.instance is not None:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():

            raise serializers.ValidationError(
                "برندی با این نام "
                "قبلاً ثبت شده است."
            )

        return value


# =========================================================
# Motorcycle Model List
# =========================================================


class MotorcycleModelListSerializer(
    serializers.ModelSerializer
):

    brand = (
        MotorcycleBrandReferenceSerializer(
            read_only=True
        )
    )

    class Meta:
        model = MotorcycleModel

        fields = [
            "id",
            "brand",
            "name",
            "slug",
            "production_start_year",
            "production_end_year",
            "engine_volume",
            "image",
        ]

        read_only_fields = fields


# =========================================================
# Motorcycle Model Detail
# =========================================================


class MotorcycleModelDetailSerializer(
    serializers.ModelSerializer
):

    brand = (
        MotorcycleBrandReferenceSerializer(
            read_only=True
        )
    )

    class Meta:
        model = MotorcycleModel

        fields = [
            "id",
            "brand",
            "name",
            "slug",
            "production_start_year",
            "production_end_year",
            "engine_volume",
            "description",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# =========================================================
# Motorcycle Model Create / Update
# =========================================================


class MotorcycleModelCreateUpdateSerializer(
    serializers.ModelSerializer
):

    slug = serializers.CharField(
        read_only=True,
    )

    brand = serializers.PrimaryKeyRelatedField(
        queryset=(
            MotorcycleBrand.objects.all()
        ),
    )

    class Meta:
        model = MotorcycleModel

        fields = [
            "brand",
            "name",
            "slug",
            "production_start_year",
            "production_end_year",
            "engine_volume",
            "description",
            "image",
            "is_active",
        ]

        read_only_fields = [
            "slug",
        ]

    # =====================================================
    # Name
    # =====================================================

    def validate_name(
        self,
        value,
    ):

        value = (
            normalize_single_line_text(
                value
            )
        )

        if not value:

            raise serializers.ValidationError(
                "نام مدل موتورسیکلت "
                "الزامی است."
            )

        return value

    # =====================================================
    # Description
    # =====================================================

    def validate_description(
        self,
        value,
    ):

        return value.strip()

    # =====================================================
    # Object Validation
    # =====================================================

    def validate(
        self,
        attrs,
    ):

        instance = self.instance

        # -------------------------------------------------
        # Brand
        # -------------------------------------------------

        brand = attrs.get(
            "brand",
            (
                instance.brand
                if instance
                else None
            ),
        )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name = attrs.get(
            "name",
            (
                instance.name
                if instance
                else None
            ),
        )

        # -------------------------------------------------
        # Duplicate Model
        # -------------------------------------------------

        if brand and name:

            queryset = (
                MotorcycleModel.objects.filter(
                    brand=brand,
                    name__iexact=name,
                )
            )

            if instance is not None:

                queryset = queryset.exclude(
                    pk=instance.pk
                )

            if queryset.exists():

                raise serializers.ValidationError(
                    {
                        "name": (
                            "این مدل برای برند "
                            "انتخاب‌شده قبلاً "
                            "ثبت شده است."
                        )
                    }
                )

        # -------------------------------------------------
        # Production Years
        # -------------------------------------------------

        start_year = attrs.get(
            "production_start_year",
            (
                instance.production_start_year
                if instance
                else None
            ),
        )

        end_year = attrs.get(
            "production_end_year",
            (
                instance.production_end_year
                if instance
                else None
            ),
        )

        if (
            start_year is not None
            and end_year is not None
            and end_year < start_year
        ):

            raise serializers.ValidationError(
                {
                    "production_end_year": (
                        "سال پایان تولید "
                        "نمی‌تواند قبل از "
                        "سال شروع تولید باشد."
                    )
                }
            )

        return attrs