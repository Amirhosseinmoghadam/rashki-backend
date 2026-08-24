from django.db import models
from django.conf import settings


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        CONFIRMED = "confirmed", "تأیید شده"
        PROCESSING = "processing", "در حال پردازش"
        SHIPPED = "shipped", "ارسال شده"
        DELIVERED = "delivered", "تحویل شده"
        CANCELLED = "cancelled", "لغو شده"
        RETURNED = "returned", "مرجوع شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    address = models.ForeignKey(
        "addresses.Address",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="آدرس",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="جمع کالاها",
    )

    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="تخفیف",
    )

    shipping_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="هزینه ارسال",
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="مبلغ نهایی",
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد تخفیف",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="یادداشت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name="نام محصول در زمان خرید",
    )

    sku = models.CharField(
        max_length=100,
        verbose_name="SKU در زمان خرید",
    )

    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="قیمت واحد",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="تعداد",
    )

    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="تخفیف",
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="مبلغ نهایی",
    )

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"