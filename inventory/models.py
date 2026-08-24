from django.db import models


class Supplier(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="نام تأمین‌کننده",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="تلفن",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
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

    def __str__(self):
        return self.name

class Purchase(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        RECEIVED = "received", "دریافت شده"
        CANCELLED = "cancelled", "لغو شده"

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
        verbose_name="تأمین‌کننده",
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شماره فاکتور",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    purchase_date = models.DateTimeField(
        verbose_name="تاریخ خرید",
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
        verbose_name = "خرید"
        verbose_name_plural = "خریدها"
        ordering = ["-purchase_date"]

    def __str__(self):
        return self.invoice_number or f"Purchase #{self.pk}"



class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="خرید",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="purchase_items",
        verbose_name="محصول",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="تعداد",
    )

    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="قیمت خرید واحد",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost

    class Meta:
        verbose_name = "آیتم خرید"
        verbose_name_plural = "آیتم‌های خرید"

    def __str__(self):
        return f"{self.variant} × {self.quantity}"

class StockMovement(models.Model):

    class MovementType(models.TextChoices):
        PURCHASE = "purchase", "خرید"
        SALE = "sale", "فروش"
        RETURN = "return", "مرجوعی"
        ADJUSTMENT = "adjustment", "اصلاح موجودی"
        DAMAGE = "damage", "خرابی"
        LOSS = "loss", "کسری"

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="stock_movements",
        verbose_name="محصول",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        verbose_name="نوع گردش",
    )

    quantity = models.IntegerField(
        verbose_name="تعداد",
        help_text="ورودی مثبت، خروجی منفی",
    )

    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="هزینه واحد",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="مرجع",
    )

    note = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "گردش موجودی"
        verbose_name_plural = "گردش موجودی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant} - {self.quantity}"