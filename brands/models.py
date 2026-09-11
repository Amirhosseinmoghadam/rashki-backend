from django.db import models

from utils.slug import generate_unique_slug
from utils.upload import upload_to
from utils.validators import validate_image


# =========================================================
# Brand
# =========================================================


class Brand(models.Model):

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
    # Additional Information
    # =====================================================

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    website = models.URLField(
        blank=True,
        verbose_name="وب‌سایت",
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
        verbose_name = "برند"
        verbose_name_plural = "برندها"

        ordering = [
            "name",
        ]

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

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