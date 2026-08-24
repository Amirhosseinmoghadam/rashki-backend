from django.db import models
from django.conf import settings


class ArticleCategory(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name

class Article(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشر شده"
        ARCHIVED = "archived", "بایگانی"

    title = models.CharField(
        max_length=255,
        verbose_name="عنوان",
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        verbose_name="اسلاگ",
    )

    excerpt = models.TextField(
        blank=True,
        verbose_name="خلاصه",
    )

    content = models.TextField(
        verbose_name="محتوا",
    )

    cover_image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True,
        verbose_name="تصویر اصلی",
    )

    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="دسته‌بندی",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="نویسنده",
    )

    products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="articles",
        verbose_name="محصولات مرتبط",
    )

    motorcycles = models.ManyToManyField(
        "motorcycles.MotorcycleModel",
        blank=True,
        related_name="articles",
        verbose_name="موتورسیکلت‌های مرتبط",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="مقاله ویژه",
    )

    reading_time = models.PositiveIntegerField(
        default=1,
        verbose_name="زمان مطالعه",
        help_text="بر حسب دقیقه",
    )

    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد بازدید",
    )

    seo_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SEO Title",
    )

    meta_description = models.CharField(
        max_length=320,
        blank=True,
        verbose_name="Meta Description",
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ انتشار",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title