from rest_framework import serializers

from brands.models import Brand

from utils.normalizers import (
    normalize_single_line_text,
)


# =========================================================
# Brand List Serializer
# =========================================================


class BrandListSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Brand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
        ]

        read_only_fields = fields


# =========================================================
# Brand Detail Serializer
# =========================================================


class BrandDetailSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Brand

        fields = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "website",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields


# =========================================================
# Brand Create / Update Serializer
# =========================================================


class BrandCreateUpdateSerializer(
    serializers.ModelSerializer
):

    # Explicit field so we can control duplicate
    # validation and Persian error messages.
    name = serializers.CharField(
        max_length=150,
        required=True,
    )

    slug = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Brand

        fields = [
            "name",
            "slug",
            "logo",
            "description",
            "website",
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

        value = normalize_single_line_text(
            value
        )

        if not value:

            raise serializers.ValidationError(
                "نام برند الزامی است."
            )

        queryset = Brand.objects.filter(
            name__iexact=value
        )

        if self.instance is not None:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():

            raise serializers.ValidationError(
                "برندی با این نام قبلاً "
                "ثبت شده است."
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