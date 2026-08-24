from django.db import models
from django.utils.text import slugify
class MotorcycleBrand(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام برند",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        verbose_name="اسلاگ",
    )

    logo = models.ImageField(
        upload_to="motorcycles/brands/",
        blank=True,
        null=True,
        verbose_name="لوگو",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "برند موتورسیکلت"
        verbose_name_plural = "برندهای موتورسیکلت"
        ordering = ["name"]

    def __str__(self):
        return self.name




class MotorcycleModel(models.Model):
    brand = models.ForeignKey(
        MotorcycleBrand,
        on_delete=models.PROTECT,
        related_name="models",
        verbose_name="برند موتور",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="مدل",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    production_start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="سال شروع تولید",
    )

    production_end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="سال پایان تولید",
    )

    engine_volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="حجم موتور",
        help_text="حجم موتور بر حسب CC",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    image = models.ImageField(
        upload_to="motorcycles/",
        null=True,
        blank=True,
        verbose_name="تصویر",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "مدل موتور"
        verbose_name_plural = "مدل‌های موتور"
        ordering = ["brand__name", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"],
                name="unique_motorcycle_model_per_brand",
            )
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.brand.name}-{self.name}",
                allow_unicode=True,
            )

        super().save(*args, **kwargs)