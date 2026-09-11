from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q

from utils.slug import generate_unique_slug
from utils.upload import upload_to
from utils.validators import validate_image



# =========================================================
# Product
# =========================================================


class Product(models.Model):

    # =====================================================
    # Choices
    # =====================================================

    class Status(models.TextChoices):

        # محصول هنوز آماده نمایش در سایت نیست.
        DRAFT = "draft", "پیش‌نویس"

        # محصول در سایت قابل نمایش است.
        ACTIVE = "active", "فعال"

        # محصول قدیمی یا حذف‌شده از فروش است،
        # ولی اطلاعات آن را برای سوابق نگه می‌داریم.
        ARCHIVED = "archived", "آرشیو شده"


    class PricingMode(models.TextChoices):

        # قیمت محصول بر اساس قیمت دلاری آن
        # و نرخ دلار فعلی محاسبه می‌شود.
        USD_BASED = "usd_based", "بر اساس دلار"

        # قیمت محصول مستقیماً به تومان وارد می‌شود
        # و تغییر نرخ دلار روی آن تأثیری ندارد.
        FIXED = "fixed", "قیمت ثابت"


    class Unit(models.TextChoices):

        # محصول به صورت عددی فروخته می‌شود.
        PIECE = "piece", "عدد"

        # محصول به صورت جفت فروخته می‌شود.
        PAIR = "pair", "جفت"

        # محصول به صورت یک ست فروخته می‌شود.
        SET = "set", "ست"

        # محصول به صورت بسته فروخته می‌شود.
        PACKAGE = "package", "بسته"


    # =====================================================
    # Main Information
    # =====================================================

    # نام اصلی محصول که در سایت نمایش داده می‌شود.
    name = models.CharField(
        max_length=250,
        verbose_name="نام محصول",
    )

    # آدرس SEO محصول.
    # فقط هنگام ایجاد محصول ساخته می‌شود و با تغییر نام
    # محصول تغییر نمی‌کند تا URL محصول ثابت باقی بماند.
    slug = models.SlugField(
        max_length=280,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    # دسته‌بندی اصلی محصول.
    # هر محصول فعلاً یک دسته‌بندی اصلی دارد.
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )

    # برند سازنده قطعه؛ مثل NGK یا DID.
    # برای محصولاتی که برند مشخص ندارند اختیاری است.
    brand = models.ForeignKey(
        "brands.Brand",
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="برند محصول",
    )

    # واحد فروش محصول.
    # مثال: عدد، جفت، ست یا بسته.
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.PIECE,
        verbose_name="واحد فروش",
    )

    # =====================================================
    # Product Codes
    # =====================================================

    # کد داخلی محصول در فروشگاه.
    # برای مدیریت محصولات و جستجوی سریع بسیار مفید است.
    # اگر فعلاً SKU نداریم می‌تواند خالی باشد.
    sku = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="SKU",
    )

    # شماره فنی اعلام‌شده توسط شرکت سازنده قطعه.
    # مانند CPR6EA-9 برای بعضی شمع‌ها.
    manufacturer_part_number = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="شماره فنی سازنده",
    )

    # کد OEM قطعه.
    # ممکن است چند محصول جایگزین یک OEM Code داشته باشند،
    # بنابراین Unique نیست.
    oem_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="کد OEM",
    )

    # بارکد محصول.
    # در صورت وجود می‌تواند برای انبار یا فروش حضوری
    # در آینده استفاده شود.
    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="بارکد",
    )

    # =====================================================
    # Description
    # =====================================================

    # توضیح کوتاه محصول برای Card و بالای صفحه Product.
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیح کوتاه",
    )

    # توضیحات کامل محصول برای صفحه جزئیات محصول.
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات کامل",
    )

    # کلمات کمکی برای جستجو.
    # مثال:
    # CG125, سی جی 125, هوندا 125
    # این فیلد مستقیماً به مشتری نمایش داده نمی‌شود.
    search_keywords = models.TextField(
        blank=True,
        verbose_name="کلمات کلیدی جستجو",
        help_text=(
            "عبارت‌های مترادف و جایگزین برای "
            "بهبود جستجوی محصول"
        ),
    )

    # =====================================================
    # Pricing
    # =====================================================

    # تعیین می‌کند قیمت محصول دلاری است
    # یا مستقیماً به تومان تعیین شده است.
    pricing_mode = models.CharField(
        max_length=20,
        choices=PricingMode.choices,
        default=PricingMode.FIXED,
        db_index=True,
        verbose_name="روش قیمت‌گذاری",
    )

    # قیمت پایه محصول به دلار.
    # فقط برای محصولاتی استفاده می‌شود که
    # pricing_mode برابر USD_BASED باشد.
    base_price_usd = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.0001")
            ),
        ],
        verbose_name="قیمت پایه دلاری",
    )

    # قیمت پایه محصول به تومان.
    # برای محصولاتی که قیمتشان مستقیماً به تومان تعیین می‌شود.
    base_price_toman = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="قیمت پایه به تومان",
    )

    # درصد افزایش قیمت روی قیمت پایه.
    # مثال:
    # اگر قیمت پایه 1,000,000 تومان و markup برابر 20 باشد،
    # 20 درصد به قیمت اضافه می‌شود.
    markup_percent = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        default=Decimal("0"),
        validators=[
            MinValueValidator(
                Decimal("0")
            ),
        ],
        verbose_name="درصد افزایش قیمت",
    )

    # هزینه ثابت اضافی روی محصول.
    # مثال: هزینه واردات، بسته‌بندی یا هزینه ثابت دیگر.
    fixed_cost_toman = models.PositiveBigIntegerField(
        default=0,
        verbose_name="هزینه ثابت اضافی به تومان",
    )

    # قیمت نهایی فعلی محصول به تومان.
    # این مقدار توسط PricingService محاسبه می‌شود
    # و Frontend، Cart و Search فقط از همین قیمت استفاده می‌کنند.
    current_price_toman = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name="قیمت نهایی فعلی به تومان",
    )

    # نرخ دلاری که آخرین بار برای محاسبه
    # current_price_toman استفاده شده است.
    # برای بررسی و گزارش‌گیری بعدی نگهداری می‌شود.
    last_exchange_rate_toman = (
        models.PositiveBigIntegerField(
            null=True,
            blank=True,
            editable=False,
            verbose_name=(
                "آخرین نرخ دلار استفاده‌شده"
            ),
        )
    )

    # زمان آخرین محاسبه قیمت محصول.
    price_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="آخرین بروزرسانی قیمت",
    )

    # اگر فعال باشد، تغییر نرخ دلار
    # قیمت این محصول را تغییر نمی‌دهد.
    # برای محصولاتی که موقتاً می‌خواهیم قیمتشان ثابت بماند.
    is_price_locked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="قفل قیمت",
    )

    # =====================================================
    # Stock
    # =====================================================

    # تعداد موجودی فعلی محصول.
    # فعلاً تا زمانی که سیستم Inventory جدا نداریم
    # موجودی را روی خود Product نگه می‌داریم.
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )

    # وقتی موجودی به این مقدار یا کمتر برسد
    # می‌توانیم در Admin هشدار کمبود موجودی نمایش دهیم.
    low_stock_threshold = models.PositiveIntegerField(
        default=3,
        verbose_name="حد هشدار موجودی",
    )

    # =====================================================
    # Shipping Information
    # =====================================================

    # وزن محصول به گرم.
    # برای محاسبه هزینه پست پیشتاز و تیپاکس استفاده می‌شود.
    weight_grams = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="وزن به گرم",
    )

    # طول بسته یا محصول به سانتی‌متر.
    length_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="طول به سانتی‌متر",
    )

    # عرض بسته یا محصول به سانتی‌متر.
    width_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="عرض به سانتی‌متر",
    )

    # ارتفاع بسته یا محصول به سانتی‌متر.
    height_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="ارتفاع به سانتی‌متر",
    )
    # =========================================================
    # Shipping / Physical Package Information
    # =========================================================

    shipping_length_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="طول بسته برای ارسال (cm)",
        help_text=(
            "طول واقعی محصول پس از آماده‌سازی برای ارسال. "
            "برای انتخاب خودکار بسته تیپاکس استفاده می‌شود."
        ),
    )

    shipping_width_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="عرض بسته برای ارسال (cm)",
    )

    shipping_height_cm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
        ],
        verbose_name="ارتفاع بسته برای ارسال (cm)",
    )

    # =====================================================
    # Motorcycle Compatibility
    # =====================================================

    # لیست موتورسیکلت‌هایی که این قطعه با آن‌ها سازگار است.
    # اطلاعات واقعی رابطه در ProductCompatibility ذخیره می‌شود.
    compatible_motorcycles = models.ManyToManyField(
        "motorcycles.MotorcycleModel",
        through="ProductCompatibility",
        related_name="compatible_products",
        blank=True,
        verbose_name="موتورسیکلت‌های سازگار",
    )

    # =====================================================
    # Related Products
    # =====================================================

    # محصولاتی که Admin به صورت دستی
    # به عنوان محصول مرتبط انتخاب می‌کند.
    related_products = models.ManyToManyField(
        "self",
        through="ProductRelation",
        through_fields=(
            "product",
            "related_product",
        ),
        symmetrical=False,
        related_name="related_from_products",
        blank=True,
        verbose_name="محصولات مرتبط",
    )

    # =====================================================
    # SEO
    # =====================================================

    # عنوان اختصاصی SEO.
    # اگر خالی باشد بعداً می‌توانیم نام محصول را استفاده کنیم.
    meta_title = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="عنوان SEO",
    )

    # توضیح Meta Description صفحه محصول.
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        verbose_name="توضیحات SEO",
    )

    # =====================================================
    # Status
    # =====================================================

    # وضعیت انتشار محصول.
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="وضعیت",
    )

    # مشخص می‌کند محصول در بخش‌های ویژه سایت
    # قابل نمایش باشد یا خیر.
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="محصول ویژه",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان ایجاد محصول.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین تغییر اطلاعات محصول.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:

        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

        ordering = [
            "-created_at",
        ]

        indexes = [

            # برای فیلتر سریع محصولات فعال بر اساس قیمت.
            models.Index(
                fields=[
                    "status",
                    "current_price_toman",
                ],
                name="product_status_price_idx",
            ),

            # برای فیلتر سریع محصولات یک دسته‌بندی.
            models.Index(
                fields=[
                    "category",
                    "status",
                ],
                name="product_category_status_idx",
            ),

            # برای فیلتر سریع محصولات یک برند.
            models.Index(
                fields=[
                    "brand",
                    "status",
                ],
                name="product_brand_status_idx",
            ),
        ]

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):

        super().clean()

        errors = {}

        # محصول دلاری حتماً باید قیمت پایه دلاری داشته باشد.
        if (
            self.pricing_mode
            == self.PricingMode.USD_BASED
            and self.base_price_usd is None
        ):
            errors[
                "base_price_usd"
            ] = (
                "برای محصول با قیمت‌گذاری دلاری "
                "وارد کردن قیمت پایه دلار الزامی است."
            )

        # محصول با قیمت ثابت حتماً باید
        # قیمت تومان داشته باشد.
        if (
            self.pricing_mode
            == self.PricingMode.FIXED
            and self.base_price_toman is None
        ):
            errors[
                "base_price_toman"
            ] = (
                "برای محصول با قیمت ثابت "
                "وارد کردن قیمت تومان الزامی است."
            )

        # محصول Active نباید بدون قیمت نهایی باشد.
        if (
            self.status
            == self.Status.ACTIVE
            and self.current_price_toman is None
        ):
            errors[
                "status"
            ] = (
                "محصول بدون قیمت نهایی "
                "نمی‌تواند فعال شود."
            )

        if errors:
            raise ValidationError(
                errors
            )

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        # حذف فاصله‌های اضافی نام محصول.
        self.name = self.name.strip()

        # مقدار خالی SKU را به NULL تبدیل می‌کنیم
        # تا Unique بودن آن مشکل ایجاد نکند.
        self.sku = (
            self.sku.strip()
            if self.sku
            else None
        )

        # مقدار خالی Barcode نیز NULL می‌شود.
        self.barcode = (
            self.barcode.strip()
            if self.barcode
            else None
        )

        # تمیز کردن شماره فنی.
        self.manufacturer_part_number = (
            self.manufacturer_part_number.strip()
        )

        # تمیز کردن OEM Code.
        self.oem_code = (
            self.oem_code.strip()
        )

        # Slug فقط اولین بار ساخته می‌شود.
        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=self.name,
            )

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        return self.name


# =========================================================
# Product Image
# =========================================================


class ProductImage(models.Model):

    # حداکثر تعداد کل تصاویر هر محصول.
    # شامل تصویر اصلی نیز می‌شود.
    MAX_IMAGES_PER_PRODUCT = 20

    # محصولی که تصویر متعلق به آن است.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول",
    )

    # فایل تصویر محصول.
    image = models.ImageField(
        upload_to=upload_to,
        validators=[
            validate_image,
        ],
        verbose_name="تصویر",
    )

    # متن جایگزین تصویر برای Accessibility و SEO.
    alt_text = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="متن جایگزین تصویر",
    )

    # مشخص می‌کند این تصویر،
    # تصویر اصلی Product است یا خیر.
    # هر محصول حداکثر یک تصویر اصلی دارد.
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="تصویر اصلی",
    )

    # ترتیب نمایش تصویر در Gallery.
    # عدد کمتر زودتر نمایش داده می‌شود.
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    # زمان ثبت تصویر.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:

        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"

        ordering = [
            "sort_order",
            "id",
        ]

        constraints = [

            # هر محصول حداکثر یک تصویر اصلی دارد.
            models.UniqueConstraint(
                fields=[
                    "product",
                ],
                condition=Q(
                    is_primary=True
                ),
                name=(
                    "unique_primary_image_"
                    "per_product"
                ),
            ),
        ]

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):

        super().clean()

        # هنگام افزودن تصویر جدید بررسی می‌کنیم
        # که تعداد تصاویر از 20 عدد بیشتر نشود.
        if (
            self._state.adding
            and self.product_id
            and ProductImage.objects.filter(
                product_id=self.product_id
            ).count()
            >= self.MAX_IMAGES_PER_PRODUCT
        ):

            raise ValidationError(
                {
                    "image": (
                        "برای هر محصول حداکثر "
                        "20 تصویر قابل ثبت است."
                    )
                }
            )

    # =====================================================
    # Save
    # =====================================================

    def save(self, *args, **kwargs):
        """
        ذخیره تصویر محصول.

        قوانین:
        1. هر محصول حداکثر 20 تصویر دارد.
        2. اولین تصویر محصول به صورت خودکار Primary می‌شود.
        3. هر محصول فقط یک Primary Image دارد.
        4. برای جلوگیری از Race Condition، هنگام افزودن
           تصویر جدید Product در PostgreSQL Lock می‌شود.
        """

        with transaction.atomic():

            # -------------------------------------------------
            # Lock Product
            # -------------------------------------------------

            if self.product_id:
                Product.objects.select_for_update().get(
                    pk=self.product_id
                )

            # -------------------------------------------------
            # Maximum Image Count
            # -------------------------------------------------

            if self._state.adding and self.product_id:

                image_count = ProductImage.objects.filter(
                    product_id=self.product_id
                ).count()

                if image_count >= self.MAX_IMAGES_PER_PRODUCT:
                    raise ValidationError(
                        {
                            "image": (
                                "برای هر محصول حداکثر "
                                "20 تصویر قابل ثبت است."
                            )
                        }
                    )

            # -------------------------------------------------
            # First Image → Primary
            # -------------------------------------------------

            if self._state.adding and self.product_id:

                has_image = ProductImage.objects.filter(
                    product_id=self.product_id
                ).exists()

                if not has_image:
                    self.is_primary = True

            # -------------------------------------------------
            # Only One Primary Image
            # -------------------------------------------------

            if self.is_primary and self.product_id:
                ProductImage.objects.filter(
                    product_id=self.product_id,
                    is_primary=True,
                ).exclude(
                    pk=self.pk
                ).update(
                    is_primary=False
                )

            # -------------------------------------------------
            # Save
            # -------------------------------------------------

            super().save(*args, **kwargs)

    # =====================================================
    # Delete
    # =====================================================

    def delete(
        self,
        *args,
        **kwargs,
    ):

        product_id = self.product_id

        # بررسی می‌کنیم آیا تصویر حذف‌شده Primary بوده است.
        was_primary = self.is_primary

        with transaction.atomic():

            result = super().delete(
                *args,
                **kwargs,
            )

            # اگر تصویر اصلی حذف شد،
            # اولین تصویر باقی‌مانده Primary می‌شود.
            if was_primary:

                next_image = (
                    ProductImage.objects
                    .filter(
                        product_id=product_id
                    )
                    .order_by(
                        "sort_order",
                        "id",
                    )
                    .first()
                )

                if next_image:

                    ProductImage.objects.filter(
                        pk=next_image.pk
                    ).update(
                        is_primary=True
                    )

        return result

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"{self.pk}"
        )


# =========================================================
# Product Attribute
# =========================================================


class ProductAttribute(models.Model):

    class DataType(models.TextChoices):

        # مقدار متنی مثل:
        # جنس = سرامیک
        TEXT = "text", "متن"

        # مقدار عددی مثل:
        # تعداد لینک = 120
        NUMBER = "number", "عدد"

        # مقدار بله / خیر.
        BOOLEAN = "boolean", "بله / خیر"

        # مقدار انتخابی از لیست مشخص.
        # مثال:
        # محل نصب = جلو / عقب
        CHOICE = "choice", "انتخابی"


    # نام ویژگی.
    # مثال: تعداد لینک، قطر، جنس، محل نصب.
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام ویژگی",
    )

    # شناسه متنی ویژگی برای API و URL.
    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    # نوع داده ویژگی.
    # تعیین می‌کند مقدار آن متن، عدد،
    # Boolean یا Choice است.
    data_type = models.CharField(
        max_length=20,
        choices=DataType.choices,
        verbose_name="نوع داده",
    )

    # واحد اندازه‌گیری ویژگی.
    # مثال: mm، cm، عدد، گرم.
    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="واحد",
    )

    # اگر True باشد این ویژگی
    # در فیلتر محصولات قابل استفاده است.
    is_filterable = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="قابل فیلتر",
    )

    # اگر True باشد مقدار این ویژگی
    # در Search محصولات نیز بررسی می‌شود.
    is_searchable = models.BooleanField(
        default=False,
        verbose_name="قابل جستجو",
    )

    # مشخص می‌کند Attribute قابل استفاده است یا خیر.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # ترتیب نمایش Attribute در صفحه Product.
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    # دسته‌بندی‌هایی که این ویژگی برای آن‌ها کاربرد دارد.
    categories = models.ManyToManyField(
        "categories.Category",
        through="CategoryAttribute",
        related_name="product_attributes",
        blank=True,
        verbose_name="دسته‌بندی‌ها",
    )

    # زمان ایجاد ویژگی.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین تغییر ویژگی.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصولات"

        ordering = [
            "sort_order",
            "name",
        ]

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.name = self.name.strip()

        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=self.name,
            )

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return self.name


# =========================================================
# Product Attribute Option
# =========================================================


class ProductAttributeOption(models.Model):

    # ویژگی‌ای که Option متعلق به آن است.
    # مثال:
    # Attribute = محل نصب
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="ویژگی",
    )

    # مقدار قابل انتخاب.
    # مثال: جلو، عقب.
    value = models.CharField(
        max_length=150,
        verbose_name="مقدار",
    )

    # Slug مقدار برای API.
    slug = models.SlugField(
        max_length=180,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    # ترتیب نمایش Optionها.
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    # مشخص می‌کند Option قابل انتخاب است یا خیر.
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:

        verbose_name = "گزینه ویژگی"
        verbose_name_plural = "گزینه‌های ویژگی"

        ordering = [
            "sort_order",
            "value",
        ]

        constraints = [

            # یک مقدار در یک Attribute
            # دوبار ثبت نمی‌شود.
            models.UniqueConstraint(
                fields=[
                    "attribute",
                    "value",
                ],
                name=(
                    "unique_attribute_option"
                ),
            ),
        ]

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.value = self.value.strip()

        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=(
                    f"{self.attribute.name} "
                    f"{self.value}"
                ),
            )

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.attribute.name}: "
            f"{self.value}"
        )


# =========================================================
# Category Attribute
# =========================================================


class CategoryAttribute(models.Model):

    # دسته‌بندی‌ای که Attribute برای آن تعریف شده است.
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        related_name="category_attributes",
        verbose_name="دسته‌بندی",
    )

    # ویژگی‌ای که به Category متصل شده است.
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="category_links",
        verbose_name="ویژگی",
    )

    # اگر True باشد هنگام ایجاد محصول
    # در این Category وارد کردن این ویژگی الزامی است.
    is_required = models.BooleanField(
        default=False,
        verbose_name="الزامی",
    )

    # ترتیب نمایش Attribute در این Category.
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:

        verbose_name = "ویژگی دسته‌بندی"
        verbose_name_plural = (
            "ویژگی‌های دسته‌بندی"
        )

        ordering = [
            "sort_order",
        ]

        constraints = [

            # یک Attribute برای یک Category
            # فقط یک بار تعریف می‌شود.
            models.UniqueConstraint(
                fields=[
                    "category",
                    "attribute",
                ],
                name=(
                    "unique_category_attribute"
                ),
            ),
        ]

    def __str__(self):

        return (
            f"{self.category} - "
            f"{self.attribute}"
        )


# =========================================================
# Product Attribute Value
# =========================================================


class ProductAttributeValue(models.Model):

    # محصولی که مقدار Attribute برای آن ثبت شده است.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name="محصول",
    )

    # Attribute موردنظر.
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.PROTECT,
        related_name="product_values",
        verbose_name="ویژگی",
    )

    # مقدار متنی Attribute.
    # فقط وقتی data_type برابر TEXT باشد استفاده می‌شود.
    value_text = models.TextField(
        blank=True,
        verbose_name="مقدار متنی",
    )

    # مقدار عددی Attribute.
    # فقط وقتی data_type برابر NUMBER باشد استفاده می‌شود.
    value_number = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="مقدار عددی",
    )

    # مقدار True/False Attribute.
    # فقط برای نوع BOOLEAN استفاده می‌شود.
    value_boolean = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="مقدار بله / خیر",
    )

    # Option انتخاب‌شده.
    # فقط وقتی data_type برابر CHOICE باشد استفاده می‌شود.
    option = models.ForeignKey(
        ProductAttributeOption,
        on_delete=models.PROTECT,
        related_name="product_values",
        null=True,
        blank=True,
        verbose_name="گزینه انتخاب‌شده",
    )

    class Meta:

        verbose_name = "مقدار ویژگی محصول"

        verbose_name_plural = (
            "مقادیر ویژگی‌های محصولات"
        )

        constraints = [

            # هر Product از هر Attribute
            # فعلاً فقط یک مقدار می‌تواند داشته باشد.
            models.UniqueConstraint(
                fields=[
                    "product",
                    "attribute",
                ],
                name=(
                    "unique_product_attribute_value"
                ),
            ),
        ]

        indexes = [

            # مناسب فیلتر Attributeهای عددی.
            models.Index(
                fields=[
                    "attribute",
                    "value_number",
                ],
                name="attribute_number_idx",
            ),

            # مناسب فیلتر Choiceها.
            models.Index(
                fields=[
                    "attribute",
                    "option",
                ],
                name="attribute_option_idx",
            ),
        ]

    def clean(self):

        super().clean()

        errors = {}

        attribute_type = (
            self.attribute.data_type
            if self.attribute_id
            else None
        )

        # Attribute متنی باید value_text داشته باشد.
        if (
            attribute_type
            == ProductAttribute.DataType.TEXT
            and not self.value_text.strip()
        ):

            errors[
                "value_text"
            ] = (
                "برای این ویژگی وارد کردن "
                "مقدار متنی الزامی است."
            )

        # Attribute عددی باید value_number داشته باشد.
        if (
            attribute_type
            == ProductAttribute.DataType.NUMBER
            and self.value_number is None
        ):

            errors[
                "value_number"
            ] = (
                "برای این ویژگی وارد کردن "
                "مقدار عددی الزامی است."
            )

        # Attribute Boolean باید True یا False داشته باشد.
        if (
            attribute_type
            == ProductAttribute.DataType.BOOLEAN
            and self.value_boolean is None
        ):

            errors[
                "value_boolean"
            ] = (
                "برای این ویژگی انتخاب "
                "بله یا خیر الزامی است."
            )

        # Attribute Choice باید Option داشته باشد.
        if (
            attribute_type
            == ProductAttribute.DataType.CHOICE
            and self.option_id is None
        ):

            errors[
                "option"
            ] = (
                "برای این ویژگی انتخاب "
                "یک گزینه الزامی است."
            )

        # Option حتماً باید متعلق به همان Attribute باشد.
        if (
            self.option_id
            and self.attribute_id
            and self.option.attribute_id
            != self.attribute_id
        ):

            errors[
                "option"
            ] = (
                "گزینه انتخاب‌شده متعلق "
                "به این ویژگی نیست."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def __str__(self):

        return (
            f"{self.product} - "
            f"{self.attribute}"
        )


# =========================================================
# Product Compatibility
# =========================================================


class ProductCompatibility(models.Model):

    # محصول موردنظر.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="compatibilities",
        verbose_name="محصول",
    )

    # مدل موتورسیکلتی که این محصول
    # با آن سازگار است.
    motorcycle = models.ForeignKey(
        "motorcycles.MotorcycleModel",
        on_delete=models.PROTECT,
        related_name="product_compatibilities",
        verbose_name="مدل موتورسیکلت",
    )

    # اگر قطعه فقط برای موتورهای تولیدشده
    # از یک سال خاص به بعد مناسب باشد.
    compatible_start_year = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "سال شروع سازگاری"
            ),
        )
    )

    # اگر قطعه فقط تا سال تولید خاصی مناسب باشد.
    compatible_end_year = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "سال پایان سازگاری"
            ),
        )
    )

    # توضیح تکمیلی درباره سازگاری.
    # مثال:
    # فقط مدل انژکتوری.
    note = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیح سازگاری",
    )

    class Meta:

        verbose_name = "سازگاری محصول"

        verbose_name_plural = (
            "سازگاری محصولات"
        )

        constraints = [

            # یک Product و Motorcycle
            # فقط یک رابطه Compatibility دارند.
            models.UniqueConstraint(
                fields=[
                    "product",
                    "motorcycle",
                ],
                name=(
                    "unique_product_motorcycle"
                ),
            ),
        ]

        indexes = [

            # برای جستجوی سریع تمام قطعات
            # سازگار با یک مدل موتور.
            models.Index(
                fields=[
                    "motorcycle",
                    "product",
                ],
                name="motorcycle_product_idx",
            ),
        ]

    def clean(self):

        super().clean()

        if (
            self.compatible_start_year
            is not None
            and self.compatible_end_year
            is not None
            and self.compatible_end_year
            < self.compatible_start_year
        ):

            raise ValidationError(
                {
                    "compatible_end_year": (
                        "سال پایان سازگاری "
                        "نمی‌تواند قبل از "
                        "سال شروع باشد."
                    )
                }
            )

    def __str__(self):

        return (
            f"{self.product} → "
            f"{self.motorcycle}"
        )


# =========================================================
# Product Relation
# =========================================================


class ProductRelation(models.Model):

    # محصول اصلی.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="relations",
        verbose_name="محصول",
    )

    # محصولی که به عنوان Related Product
    # به محصول اصلی پیشنهاد می‌شود.
    related_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="related_relations",
        verbose_name="محصول مرتبط",
    )

    # ترتیب نمایش محصولات مرتبط.
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
    )

    class Meta:

        verbose_name = "محصول مرتبط"
        verbose_name_plural = "محصولات مرتبط"

        ordering = [
            "sort_order",
            "id",
        ]

        constraints = [

            # یک رابطه تکراری بین دو Product
            # ثبت نمی‌شود.
            models.UniqueConstraint(
                fields=[
                    "product",
                    "related_product",
                ],
                name=(
                    "unique_product_relation"
                ),
            ),
        ]

    def clean(self):

        super().clean()

        # یک Product نمی‌تواند Related Product خودش باشد.
        if (
            self.product_id
            and self.related_product_id
            and self.product_id
            == self.related_product_id
        ):

            raise ValidationError(
                {
                    "related_product": (
                        "یک محصول نمی‌تواند "
                        "محصول مرتبط خودش باشد."
                    )
                }
            )

    def __str__(self):

        return (
            f"{self.product} → "
            f"{self.related_product}"
        )