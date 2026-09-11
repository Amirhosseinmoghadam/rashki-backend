from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


# =========================================================
# Cart
# =========================================================


class Cart(models.Model):

    # هر User فقط یک Cart فعال دارد.
    #
    # چون Cart بعد از ثبت Order پاک می‌شود،
    # نیازی به چند Cart یا Status نداریم.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="کاربر",
    )

    # کد تخفیفی که فعلاً روی Cart انتخاب شده است.
    #
    # مبلغ تخفیف ذخیره نمی‌شود چون ممکن است:
    #
    # - مبلغ Cart تغییر کند
    # - کد منقضی شود
    # - محدودیت مصرف تغییر کند
    #
    # بنابراین هر بار اعتبار آن دوباره بررسی می‌شود.
    applied_discount = models.ForeignKey(
        "discounts.DiscountCode",
        on_delete=models.SET_NULL,
        related_name="carts",
        null=True,
        blank=True,
        verbose_name="کد تخفیف اعمال‌شده",
    )

    # زمان ساخته‌شدن Cart.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین تغییر Cart.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):

        return (
            f"Cart #{self.pk} - "
            f"{self.user}"
        )


# =========================================================
# Cart Item
# =========================================================


class CartItem(models.Model):

    # Cartی که Item متعلق به آن است.
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید",
    )

    # Product موجود در Cart.
    #
    # اگر Product در Development کاملاً حذف شود،
    # Item مربوط به آن نیز حذف می‌شود.
    #
    # در آینده OrderItem مستقل از این رابطه
    # Snapshot خودش را خواهد داشت.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="محصول",
    )

    # تعداد محصول در Cart.
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="تعداد",
    )

    # زمان اضافه‌شدن Product به Cart.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن",
    )

    # زمان آخرین تغییر Quantity.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "آیتم سبد خرید"

        verbose_name_plural = (
            "آیتم‌های سبد خرید"
        )

        ordering = [
            "created_at",
            "id",
        ]

        constraints = [

            # یک Product در یک Cart
            # فقط یک CartItem دارد.
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "product",
                ],
                name=(
                    "unique_product_per_cart"
                ),
            ),

            # حتی در سطح DB، Quantity
            # نباید صفر یا منفی باشد.
            models.CheckConstraint(
                condition=Q(
                    quantity__gte=1
                ),
                name=(
                    "cart_item_quantity_gte_1"
                ),
            ),
        ]

    def __str__(self):

        return (
            f"{self.product} × "
            f"{self.quantity}"
        )