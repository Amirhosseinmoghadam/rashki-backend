from django.conf import settings
from django.db import models


# =========================================================
# Wishlist Item
# =========================================================


class WishlistItem(models.Model):

    # کاربری که محصول را به علاقه‌مندی‌های خود
    # اضافه کرده است.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="کاربر",
    )

    # محصولی که کاربر به علاقه‌مندی‌ها اضافه کرده است.
    #
    # اگر Product کاملاً از سیستم حذف شود،
    # WishlistItem مربوط به آن نیز حذف می‌شود.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="محصول",
    )

    # زمانی که محصول به Wishlist اضافه شده است.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن",
    )

    class Meta:

        verbose_name = "محصول مورد علاقه"

        verbose_name_plural = (
            "محصولات مورد علاقه"
        )

        # جدیدترین محصول ذخیره‌شده
        # در ابتدای Wishlist نمایش داده می‌شود.
        ordering = [
            "-created_at",
        ]

        constraints = [

            # هر کاربر فقط یک بار می‌تواند
            # یک Product مشخص را به Wishlist اضافه کند.
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product",
                ],
                name=(
                    "unique_wishlist_product_"
                    "per_user"
                ),
            ),
        ]

        indexes = [

            # برای دریافت سریع Wishlist هر کاربر
            # به ترتیب تاریخ.
            models.Index(
                fields=[
                    "user",
                    "-created_at",
                ],
                name="wishlist_user_date_idx",
            ),
        ]

    def __str__(self):

        return (
            f"{self.user} → "
            f"{self.product}"
        )