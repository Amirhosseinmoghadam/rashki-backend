from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

# =========================================================
# Product
# =========================================================


class Product(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="نام محصول",
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    brand = models.ForeignKey(
        "brands.Brand",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="برند",
    )

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )

    short_description = models.TextField(
        blank=True,
        verbose_name="توضیحات کوتاه",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات کامل",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="ویژه",
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
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


# =========================================================
# Product Images
# =========================================================


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول",
    )

    image = models.ImageField(
        upload_to="products/images/",
        verbose_name="تصویر",
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="متن جایگزین",
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان تصویر",
    )

    is_primary = models.BooleanField(
        default=False,
        verbose_name="تصویر اصلی",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True,
            ).exclude(
                pk=self.pk,
            ).update(
                is_primary=False,
            )

        super().save(*args, **kwargs)


# =========================================================
# Attribute Group
# =========================================================


class AttributeGroup(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام گروه",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "گروه ویژگی"
        verbose_name_plural = "گروه‌های ویژگی"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


# =========================================================
# Attribute
# =========================================================


class Attribute(models.Model):

    class ValueType(models.TextChoices):
        TEXT = "text", "متن"
        NUMBER = "number", "عدد"
        BOOLEAN = "boolean", "بله/خیر"
        CHOICE = "choice", "انتخابی"

    group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.PROTECT,
        related_name="attributes",
        verbose_name="گروه",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="نام ویژگی",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    value_type = models.CharField(
        max_length=20,
        choices=ValueType.choices,
        default=ValueType.TEXT,
        verbose_name="نوع مقدار",
    )

    unit = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="واحد",
        help_text="مثلاً mm، kg، CC",
    )

    is_filterable = models.BooleanField(
        default=False,
        verbose_name="قابل استفاده در فیلتر",
    )

    is_required = models.BooleanField(
        default=False,
        verbose_name="اجباری",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی‌ها"
        ordering = ["group", "sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


# =========================================================
# Attribute Value
# =========================================================


class AttributeValue(models.Model):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name="ویژگی",
    )

    value = models.CharField(
        max_length=150,
        verbose_name="مقدار",
    )

    slug = models.SlugField(
        max_length=180,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی‌ها"
        ordering = ["sort_order", "value"]

        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_value",
            )
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.value,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


# =========================================================
# Product Attribute Value
# =========================================================


class ProductAttributeValue(models.Model):
    """
    ویژگی‌هایی که به خود Product تعلق دارند
    و بین تمام Variantهای محصول مشترک هستند.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name="محصول",
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT,
        related_name="product_values",
        verbose_name="ویژگی",
    )

    value = models.TextField(
        verbose_name="مقدار",
    )

    class Meta:
        verbose_name = "مقدار ویژگی محصول"
        verbose_name_plural = "مقادیر ویژگی محصولات"

        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute"],
                name="unique_product_attribute",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - " f"{self.attribute.name}: " f"{self.value}"


# =========================================================
# Product Variant
# =========================================================


class ProductVariant(models.Model):
    """
    هر Variant یک واحد قابل فروش مستقل است.

    قیمت و موجودی در این مدل قرار دارند،
    نه در Product.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="محصول",
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="نام تنوع",
        help_text="مثلاً: CG125 - جلو - مشکی",
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="SKU",
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="قیمت فروش",
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
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
        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع‌های محصول"
        ordering = ["id"]

    def __str__(self):
        return self.name or f"{self.product.name} - {self.sku}"

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def is_available(self):
        return self.is_active and self.stock > 0


# =========================================================
# Variant Attribute Value
# =========================================================


class VariantAttributeValue(models.Model):
    """
    ویژگی‌هایی که مختص یک Variant هستند.

    مثال:
    Variant:
        CG125 - جلو - مشکی

    Attributes:
        مدل موتور = CG125
        محل نصب = جلو
        رنگ = مشکی
    """

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name="تنوع محصول",
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.PROTECT,
        related_name="variant_values",
        verbose_name="ویژگی",
    )

    value = models.ForeignKey(
        AttributeValue,
        on_delete=models.PROTECT,
        related_name="variant_values",
        verbose_name="مقدار",
    )

    class Meta:
        verbose_name = "ویژگی تنوع محصول"
        verbose_name_plural = "ویژگی‌های تنوع محصولات"

        constraints = [
            models.UniqueConstraint(
                fields=["variant", "attribute"],
                name="unique_variant_attribute",
            )
        ]

    def clean(self):
        if self.value_id and self.attribute_id:
            if self.value.attribute_id != self.attribute_id:
                raise ValidationError(
                    {"value": ("مقدار انتخاب شده " "متعلق به این ویژگی نیست.")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant} - " f"{self.attribute.name}: " f"{self.value.value}"


# =========================================================
# Product Motorcycle Compatibility
# =========================================================


class ProductMotorcycleCompatibility(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="motorcycle_compatibilities",
        verbose_name="محصول",
    )

    motorcycle = models.ForeignKey(
        "motorcycles.MotorcycleModel",
        on_delete=models.PROTECT,
        related_name="product_compatibilities",
        verbose_name="موتورسیکلت",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="یادداشت",
    )

    class Meta:
        verbose_name = "سازگاری محصول"
        verbose_name_plural = "سازگاری‌های محصولات"

        constraints = [
            models.UniqueConstraint(
                fields=["product", "motorcycle"],
                name="unique_product_motorcycle",
            )
        ]

    def __str__(self):
        return f"{self.product} ↔ {self.motorcycle}"
