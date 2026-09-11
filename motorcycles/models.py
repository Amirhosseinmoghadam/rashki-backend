from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from utils.slug import generate_unique_slug
from utils.upload import upload_to
from utils.validators import validate_image


# =========================================================
# Motorcycle Brand
# =========================================================


class MotorcycleBrand(models.Model):

    # =====================================================
    # Main Information
    # =====================================================

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام برند",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    # =====================================================
    # Media
    # =====================================================

    logo = models.ImageField(
        upload_to=upload_to,
        validators=[
            validate_image,
        ],
        blank=True,
        null=True,
        verbose_name="لوگو",
    )

    # =====================================================
    # Status
    # =====================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # =====================================================
    # Dates
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:
        verbose_name = "برند موتورسیکلت"

        verbose_name_plural = (
            "برندهای موتورسیکلت"
        )

        ordering = [
            "name",
        ]

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):

        super().clean()

        if not self.name:
            return

        self.name = self.name.strip()

        queryset = (
            MotorcycleBrand.objects.filter(
                name__iexact=self.name
            )
        )

        if self.pk:
            queryset = queryset.exclude(
                pk=self.pk
            )

        if queryset.exists():
            raise ValidationError(
                {
                    "name": (
                        "برندی با این نام "
                        "قبلاً ثبت شده است."
                    )
                }
            )

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.name = self.name.strip()

        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=self.name,
            )

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        return self.name


# =========================================================
# Motorcycle Model
# =========================================================


class MotorcycleModel(models.Model):

    # =====================================================
    # Brand
    # =====================================================

    brand = models.ForeignKey(
        MotorcycleBrand,
        on_delete=models.PROTECT,
        related_name="models",
        verbose_name="برند موتورسیکلت",
    )

    # =====================================================
    # Main Information
    # =====================================================

    name = models.CharField(
        max_length=150,
        verbose_name="مدل",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    # =====================================================
    # Production
    # =====================================================

    production_start_year = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name="سال شروع تولید",
        )
    )

    production_end_year = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name="سال پایان تولید",
        )
    )

    engine_volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="حجم موتور",
        help_text="حجم موتور بر حسب CC",
    )

    # =====================================================
    # Additional Information
    # =====================================================

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    image = models.ImageField(
        upload_to=upload_to,
        validators=[
            validate_image,
        ],
        null=True,
        blank=True,
        verbose_name="تصویر",
    )

    # =====================================================
    # Status
    # =====================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # =====================================================
    # Dates
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:
        verbose_name = "مدل موتورسیکلت"

        verbose_name_plural = (
            "مدل‌های موتورسیکلت"
        )

        ordering = [
            "brand__name",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "brand",
                    "name",
                ],
                name=(
                    "unique_motorcycle_model_"
                    "per_brand"
                ),
            ),
        ]

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):

        super().clean()

        if self.name:
            self.name = self.name.strip()

        if (
            self.production_start_year
            is not None
            and self.production_end_year
            is not None
            and self.production_end_year
            < self.production_start_year
        ):
            raise ValidationError(
                {
                    "production_end_year": (
                        "سال پایان تولید نمی‌تواند "
                        "قبل از سال شروع تولید باشد."
                    )
                }
            )

        if (
            self.brand_id
            and self.name
        ):

            queryset = (
                MotorcycleModel.objects.filter(
                    brand_id=self.brand_id,
                    name__iexact=self.name,
                )
            )

            if self.pk:
                queryset = queryset.exclude(
                    pk=self.pk
                )

            if queryset.exists():
                raise ValidationError(
                    {
                        "name": (
                            "این مدل برای برند "
                            "انتخاب‌شده قبلاً "
                            "ثبت شده است."
                        )
                    }
                )

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.name = self.name.strip()

        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=(
                    f"{self.brand.name} "
                    f"{self.name}"
                ),
            )

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        return (
            f"{self.brand.name} "
            f"{self.name}"
        )