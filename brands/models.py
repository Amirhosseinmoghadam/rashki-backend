from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
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
        upload_to="brands/",
        blank=True,
        null=True,
        verbose_name="لوگو",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    website = models.URLField(
        blank=True,
        verbose_name="وب‌سایت",
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
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["name"]

    def __str__(self):
        return self.name
