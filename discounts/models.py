from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Discount(models.Model):

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "درصدی"
        FIXED = "fixed", "مبلغ ثابت"

    name = models.CharField(
        max_length=200,
        verbose_name="نام تخفیف",
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        verbose_name="نوع تخفیف",
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name="مقدار تخفیف",
    )

    products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="discounts",
        verbose_name="محصولات",
    )

    categories = models.ManyToManyField(
        "categories.Category",
        blank=True,
        related_name="discounts",
        verbose_name="دسته‌بندی‌ها",
    )

    starts_at = models.DateTimeField(
        verbose_name="شروع",
    )

    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="پایان",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class Coupon(models.Model):

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تخفیف",
    )

    discount_type = models.CharField(
        max_length=20,
        choices=Discount.DiscountType.choices,
        verbose_name="نوع تخفیف",
    )

    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name="مقدار",
    )

    minimum_order_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="حداقل مبلغ سفارش",
    )

    maximum_discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="حداکثر مبلغ تخفیف",
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="محدودیت استفاده",
    )

    usage_limit_per_user = models.PositiveIntegerField(
        default=1,
        verbose_name="محدودیت استفاده برای هر کاربر",
    )

    starts_at = models.DateTimeField(
        verbose_name="شروع",
    )

    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="پایان",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.code
