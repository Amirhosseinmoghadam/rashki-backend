from django.db import models


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESS = "success", "موفق"
        FAILED = "failed", "ناموفق"
        CANCELLED = "cancelled", "لغو شده"

    class Gateway(models.TextChoices):
        ZARINPAL = "zarinpal", "زرین پال"
        IDPAY = "idpay", "آیدی پی"
        OTHER = "other", "سایر"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="سفارش",
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="مبلغ",
    )

    gateway = models.CharField(
        max_length=30,
        choices=Gateway.choices,
        verbose_name="درگاه",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )

    authority = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Authority",
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="شماره تراکنش",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پرداخت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.order} - {self.amount}"