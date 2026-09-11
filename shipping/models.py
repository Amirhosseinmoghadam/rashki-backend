
from django.core.validators import MinValueValidator

from django.utils import timezone


from django.core.exceptions import ValidationError
from django.db import models, transaction

from addresses.models import Province, City

# =========================================================
# Shipping Settings
# =========================================================

# =========================================================
# Tipax Settings
# =========================================================


class TipaxSettings(models.Model):

    # =====================================================
    # Payment Type
    # =====================================================

    class PaymentType(
        models.IntegerChoices
    ):

        SENDER_CREDIT = (
            10,
            "سمت فرستنده - اعتباری",
        )

        RECEIVER_POSTPAID = (
            20,
            "سمت گیرنده - پس‌کرایه",
        )

        RECEIVER_COD = (
            30,
            "سمت گیرنده - پرداخت در محل",
        )

        SENDER_COD_WITH_CREDIT = (
            40,
            "سمت فرستنده - پرداخت در محل از اعتبار",
        )

        SENDER_WALLET = (
            50,
            "سمت فرستنده - پرداخت از کیف پول",
        )

        SENDER_CASH = (
            80,
            "سمت فرستنده - نقدی",
        )

        SENDER_BRANCH_CREDIT = (
            90,
            "سمت فرستنده - اعتبار نمایندگی",
        )

        CASH_AND_PAY_IN_PLACE = (
            100,
            "نقدی - پس‌کرایه",
        )

    # =====================================================
    # Pickup Type
    # =====================================================

    class PickupType(
        models.IntegerChoices
    ):

        CUSTOMER_LOCATION = (
            10,
            "جمع‌آوری در محل مشتری",
        )

        BRANCH = (
            20,
            "تحویل در نمایندگی",
        )

    # =====================================================
    # Distribution Type
    # =====================================================

    class DistributionType(
        models.IntegerChoices
    ):

        CUSTOMER_LOCATION = (
            10,
            "تحویل در محل گیرنده",
        )

        BRANCH = (
            20,
            "تحویل در نمایندگی",
        )

    # =====================================================
    # Operational Settings
    # =====================================================

    payment_type = models.PositiveSmallIntegerField(
        choices=PaymentType.choices,
        default=PaymentType.SENDER_CREDIT,
        verbose_name="نوع پرداخت هزینه تیپاکس",
    )

    pickup_type = models.PositiveSmallIntegerField(
        choices=PickupType.choices,
        default=PickupType.CUSTOMER_LOCATION,
        verbose_name="نوع جمع‌آوری",
    )

    distribution_type = models.PositiveSmallIntegerField(
        choices=DistributionType.choices,
        default=DistributionType.CUSTOMER_LOCATION,
        verbose_name="نوع تحویل",
    )

    # اگر ShippingMethod.service_code عدد نباشد،
    # این مقدار به عنوان serviceId استفاده می‌شود.
    default_service_id = models.PositiveSmallIntegerField(
        default=2,
        verbose_name="سرویس پیش‌فرض تیپاکس",
    )

    enable_label_privacy = models.BooleanField(
        default=False,
        verbose_name="مخفی کردن اطلاعات روی لیبل",
    )

    # =====================================================
    # Tipax Customer Information
    # =====================================================

    customer_substation_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="کد شعبه مشتری",
    )

    customer_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Customer ID در تیپاکس",
    )

    # =====================================================
    # Sender Information
    # =====================================================

    sender_full_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="نام کامل فرستنده",
    )

    sender_mobile = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="موبایل فرستنده",
    )

    sender_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="تلفن فرستنده",
    )

    # =====================================================
    # Origin Address
    # =====================================================

    origin_full_address = models.TextField(
        blank=True,
        verbose_name="آدرس کامل مبدا",
    )

    origin_postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="کد پستی مبدا",
    )

    origin_floor = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="طبقه مبدا",
    )

    origin_unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="واحد مبدا",
    )

    origin_no = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="پلاک مبدا",
    )

    origin_latitude = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Latitude مبدا",
    )

    origin_longitude = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Longitude مبدا",
    )

    origin_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیحات مبدا",
    )

    # =====================================================
    # Dates
    # =====================================================

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "تنظیمات تیپاکس"
        verbose_name_plural = "تنظیمات تیپاکس"

    # =====================================================
    # Singleton
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        # فقط یک رکورد Settings داریم.
        self.pk = 1

        super().save(
            *args,
            **kwargs,
        )

    def delete(
        self,
        *args,
        **kwargs,
    ):
        # تنظیمات اصلی تیپاکس حذف نمی‌شود.
        return

    @classmethod
    def load(cls):

        obj, _ = cls.objects.get_or_create(
            pk=1,
        )

        return obj

    def __str__(self):

        return "تنظیمات تیپاکس"


class ShippingSettings(models.Model):

    # شهر مبدا ارسال فروشگاه.
    #
    # برای محاسبات تعرفه دستی فعلی الزاماً استفاده نمی‌شود،
    # ولی هنگام اتصال واقعی به API پست یا تیپاکس
    # مبدا ارسال موردنیاز خواهد بود.
    origin_city = models.ForeignKey(
        "addresses.City",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="شهر مبدا ارسال",
    )

    # وزن تقریبی بسته‌بندی که به مجموع وزن کالاها
    # اضافه می‌شود.
    #
    # مثال:
    # کارتن + ضربه‌گیر = 150 گرم
    package_extra_weight_grams = (
        models.PositiveIntegerField(
            default=150,
            verbose_name=(
                "وزن اضافه بسته‌بندی به گرم"
            ),
        )
    )

    # زمان آخرین تغییر تنظیمات.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "تنظیمات ارسال"
        verbose_name_plural = "تنظیمات ارسال"

    def save(
        self,
        *args,
        **kwargs,
    ):

        # این Model فقط یک رکورد دارد.
        self.pk = 1

        super().save(
            *args,
            **kwargs,
        )

    def delete(
        self,
        *args,
        **kwargs,
    ):
        # تنظیمات اصلی Shipping حذف نمی‌شوند.
        return

    @classmethod
    def load(cls):

        settings_obj, _ = (
            cls.objects.get_or_create(
                pk=1
            )
        )

        return settings_obj

    def __str__(self):

        return "تنظیمات ارسال"


# =========================================================
# Shipping Method
# =========================================================


class ShippingMethod(models.Model):

    class Provider(models.TextChoices):

        # شرکت ملی پست.
        POST = (
            "post",
            "شرکت ملی پست",
        )

        # تیپاکس.
        TIPAX = (
            "tipax",
            "تیپاکس",
        )

        # Provider داخلی یا سفارشی آینده.
        CUSTOM = (
            "custom",
            "سفارشی",
        )


    class CalculationMode(
        models.TextChoices
    ):

        # قیمت از جدول تعرفه‌های داخلی
        # خودمان محاسبه می‌شود.
        MANUAL = (
            "manual",
            "تعرفه دستی",
        )

        # قیمت از API شرکت حمل‌ونقل
        # دریافت می‌شود.
        API = (
            "api",
            "API",
        )


    # کد ثابت و یکتای روش ارسال.
    #
    # مثال:
    # post-pishtaz
    # tipax-standard
    code = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="کد روش ارسال",
    )

    # نامی که کاربر در Checkout می‌بیند.
    #
    # مثال:
    # پست پیشتاز
    name = models.CharField(
        max_length=150,
        verbose_name="نام روش ارسال",
    )

    # شرکت ارائه‌دهنده سرویس.
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        db_index=True,
        verbose_name="شرکت حمل‌ونقل",
    )

    # کد سرویس در داخل Provider.
    #
    # فعلاً صرفاً شناسه داخلی است.
    #
    # مثال:
    # PISHTAZ
    # STANDARD
    service_code = models.CharField(
        max_length=100,
        verbose_name="کد سرویس",
    )

    # نحوه محاسبه قیمت.
    calculation_mode = models.CharField(
        max_length=20,
        choices=CalculationMode.choices,
        default=CalculationMode.MANUAL,
        db_index=True,
        verbose_name="روش محاسبه هزینه",
    )

    # توضیح کوتاهی که مشتری در Checkout می‌بیند.
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیحات",
    )

    # حداقل زمان تقریبی تحویل.
    estimated_min_days = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "حداقل زمان تحویل به روز"
            ),
        )
    )

    # حداکثر زمان تقریبی تحویل.
    estimated_max_days = (
        models.PositiveSmallIntegerField(
            null=True,
            blank=True,
            verbose_name=(
                "حداکثر زمان تحویل به روز"
            ),
        )
    )

    # مشخص می‌کند این روش در Checkout
    # قابل انتخاب است یا خیر.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # ترتیب نمایش در Checkout.
    sort_order = (
        models.PositiveSmallIntegerField(
            default=0,
            verbose_name="ترتیب نمایش",
        )
    )

    # زمان ایجاد.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین تغییر.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "روش ارسال"
        verbose_name_plural = "روش‌های ارسال"

        ordering = [
            "sort_order",
            "id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "service_code",
                ],
                name=(
                    "unique_shipping_"
                    "provider_service"
                ),
            ),
        ]

    def clean(self):

        super().clean()

        if (
            self.estimated_min_days
            is not None
            and self.estimated_max_days
            is not None
            and self.estimated_max_days
            < self.estimated_min_days
        ):

            raise ValidationError(
                {
                    "estimated_max_days": (
                        "حداکثر زمان تحویل "
                        "نمی‌تواند کمتر از "
                        "حداقل زمان باشد."
                    )
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.code = (
            self.code
            .strip()
            .lower()
        )

        self.service_code = (
            self.service_code
            .strip()
            .upper()
        )

        self.name = (
            self.name.strip()
        )

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return self.name


# =========================================================
# Shipping Rate Rule
# =========================================================


class ShippingRateRule(models.Model):

    class DestinationScope(
        models.TextChoices
    ):

        # تعرفه عمومی برای کل کشور.
        NATIONWIDE = (
            "nationwide",
            "کل کشور",
        )

        # تعرفه مختص یک استان.
        PROVINCE = (
            "province",
            "استان",
        )

        # تعرفه مختص یک شهر.
        CITY = (
            "city",
            "شهر",
        )


    # روش ارسالی که این تعرفه متعلق به آن است.
    method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.CASCADE,
        related_name="rate_rules",
        verbose_name="روش ارسال",
    )

    # محدوده جغرافیایی Rule.
    destination_scope = models.CharField(
        max_length=20,
        choices=DestinationScope.choices,
        default=DestinationScope.NATIONWIDE,
        db_index=True,
        verbose_name="محدوده مقصد",
    )

    # اگر Scope برابر Province باشد،
    # استان مقصد در این فیلد تعیین می‌شود.
    province = models.ForeignKey(
        "addresses.Province",
        on_delete=models.CASCADE,
        related_name="shipping_rate_rules",
        null=True,
        blank=True,
        verbose_name="استان مقصد",
    )

    # اگر Scope برابر City باشد،
    # شهر مقصد در این فیلد تعیین می‌شود.
    city = models.ForeignKey(
        "addresses.City",
        on_delete=models.CASCADE,
        related_name="shipping_rate_rules",
        null=True,
        blank=True,
        verbose_name="شهر مقصد",
    )

    # حداقل وزن مرسوله‌ای که این Rule
    # برای آن معتبر است.
    min_weight_grams = (
        models.PositiveIntegerField(
            default=0,
            verbose_name="حداقل وزن به گرم",
        )
    )

    # حداکثر وزن.
    #
    # اگر Null باشد یعنی سقف وزنی ندارد.
    max_weight_grams = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name="حداکثر وزن به گرم",
        )
    )

    # هزینه پایه ارسال به تومان.
    base_price_toman = (
        models.PositiveBigIntegerField(
            validators=[
                MinValueValidator(0),
            ],
            verbose_name="هزینه پایه به تومان",
        )
    )

    # تا این وزن، هزینه پایه کافی است.
    #
    # مثال:
    # 1000
    #
    # یعنی هزینه Base تا وزن یک کیلوگرم.
    included_weight_grams = (
        models.PositiveIntegerField(
            default=1000,
            verbose_name=(
                "وزن شامل هزینه پایه به گرم"
            ),
        )
    )

    # هزینه هر کیلوگرم اضافه به تومان.
    #
    # محاسبه به صورت سقفی انجام می‌شود.
    #
    # 1.2kg اضافه = 2 کیلو اضافه
    additional_per_kg_toman = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name=(
                "هزینه هر کیلو اضافه به تومان"
            ),
        )
    )

    # اولویت Rule.
    #
    # اگر چند Rule معتبر برای یک مقصد و وزن
    # وجود داشته باشد، عدد بزرگ‌تر مقدم است.
    priority = models.IntegerField(
        default=0,
        db_index=True,
        verbose_name="اولویت",
    )

    # زمان شروع اعتبار تعرفه.
    effective_from = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="شروع اعتبار تعرفه",
    )

    # زمان پایان اعتبار تعرفه.
    #
    # Null یعنی بدون تاریخ پایان.
    effective_to = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="پایان اعتبار تعرفه",
    )

    # فعال یا غیرفعال بودن Rule.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # توضیح داخلی برای Admin.
    note = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="یادداشت",
    )

    # زمان ایجاد.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان تغییر.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "تعرفه ارسال"
        verbose_name_plural = "تعرفه‌های ارسال"

        ordering = [
            "-priority",
            "-effective_from",
        ]

        indexes = [
            models.Index(
                fields=[
                    "method",
                    "destination_scope",
                    "is_active",
                ],
                name="shipping_rule_method_idx",
            ),

            models.Index(
                fields=[
                    "method",
                    "min_weight_grams",
                    "max_weight_grams",
                ],
                name="shipping_rule_weight_idx",
            ),
        ]

    def clean(self):

        super().clean()

        errors = {}

        # ---------------------------------------------
        # Scope
        # ---------------------------------------------

        if (
            self.destination_scope
            == self.DestinationScope.NATIONWIDE
        ):

            if (
                self.province_id
                or self.city_id
            ):

                errors[
                    "destination_scope"
                ] = (
                    "برای تعرفه کل کشور نباید "
                    "استان یا شهر مشخص شود."
                )

        elif (
            self.destination_scope
            == self.DestinationScope.PROVINCE
        ):

            if not self.province_id:

                errors[
                    "province"
                ] = (
                    "برای تعرفه استانی "
                    "انتخاب استان الزامی است."
                )

            if self.city_id:

                errors[
                    "city"
                ] = (
                    "برای تعرفه استانی "
                    "شهر نباید مشخص شود."
                )

        elif (
            self.destination_scope
            == self.DestinationScope.CITY
        ):

            if not self.city_id:

                errors[
                    "city"
                ] = (
                    "برای تعرفه شهری "
                    "انتخاب شهر الزامی است."
                )

            if self.province_id:

                errors[
                    "province"
                ] = (
                    "برای تعرفه شهری "
                    "نیازی به انتخاب استان نیست."
                )

        # ---------------------------------------------
        # Weight
        # ---------------------------------------------

        if (
            self.max_weight_grams
            is not None
            and self.max_weight_grams
            < self.min_weight_grams
        ):

            errors[
                "max_weight_grams"
            ] = (
                "حداکثر وزن نمی‌تواند "
                "کمتر از حداقل وزن باشد."
            )

        # ---------------------------------------------
        # Date
        # ---------------------------------------------

        if (
            self.effective_to is not None
            and self.effective_to
            <= self.effective_from
        ):

            errors[
                "effective_to"
            ] = (
                "پایان اعتبار باید بعد "
                "از شروع اعتبار باشد."
            )

        if errors:

            raise ValidationError(
                errors
            )

    def __str__(self):

        return (
            f"{self.method} - "
            f"{self.get_destination_scope_display()}"
        )

# =========================================================
# Shipping Provider City Mapping
# =========================================================


class ShippingProviderCityMap(models.Model):

    # Provider موردنظر.
    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
        verbose_name="شرکت حمل‌ونقل",
    )

    # City داخلی پروژه ما.
    city = models.ForeignKey(
        "addresses.City",
        on_delete=models.CASCADE,
        related_name="shipping_provider_mappings",
        verbose_name="شهر",
    )

    # ID همین شهر در سیستم Provider.
    #
    # مثال:
    # City تهران در Tipax ممکن است ID مخصوص
    # خودش را داشته باشد.
    provider_city_id = (
        models.PositiveBigIntegerField(
            verbose_name="شناسه شهر در Provider",
        )
    )

    # نام شهر در Provider فقط برای Debug/Admin.
    provider_city_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="نام شهر در Provider",
    )

    # Mapping فعال باشد یا خیر.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
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

        verbose_name = "نگاشت شهر حمل‌ونقل"

        verbose_name_plural = (
            "نگاشت شهرهای حمل‌ونقل"
        )

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "provider",
                    "city",
                ],
                name=(
                    "unique_shipping_provider_city"
                ),
            ),

            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_city_id",
                ],
                name=(
                    "unique_provider_remote_city"
                ),
            ),
        ]

    def __str__(self):

        return (
            f"{self.city} → "
            f"{self.provider}: "
            f"{self.provider_city_id}"
        )

# =========================================================
# Tipax Settings
# =========================================================


class PaymentType(
    models.IntegerChoices
):

    SENDER_CREDIT = (
        10,
        "سمت فرستنده - اعتباری",
    )

    RECEIVER_POSTPAID = (
        20,
        "سمت گیرنده - پس‌کرایه",
    )

    RECEIVER_COD = (
        30,
        "سمت گیرنده - پرداخت در محل",
    )

    SENDER_COD_WITH_CREDIT = (
        40,
        "سمت فرستنده - پرداخت در محل از اعتبار",
    )

    SENDER_WALLET = (
        50,
        "سمت فرستنده - پرداخت از کیف پول",
    )

    SENDER_CASH = (
        80,
        "سمت فرستنده - نقدی",
    )

    SENDER_BRANCH_CREDIT = (
        90,
        "سمت فرستنده - اعتبار نمایندگی",
    )

    CASH_AND_PAY_IN_PLACE = (
        100,
        "نقدی - پس‌کرایه",
    )

# =========================================================
# Tipax Package Profile
# =========================================================


class TipaxPackageProfile(models.Model):

    class PackType(
        models.IntegerChoices
    ):

        ENVELOPE = (
            10,
            "پاکت",
        )

        PACKAGE = (
            20,
            "بسته",
        )

        MINI_PACK = (
            50,
            "مینی پک",
        )


    # عنوان داخلی.
    title = models.CharField(
        max_length=150,
        verbose_name="عنوان",
    )

    # بازه وزنی که این Profile برای آن استفاده می‌شود.
    min_weight_grams = (
        models.PositiveIntegerField(
            default=0,
            verbose_name="حداقل وزن به گرم",
        )
    )

    max_weight_grams = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            verbose_name="حداکثر وزن به گرم",
        )
    )

    # ابعاد بسته‌ای که به Tipax ارسال می‌شود.
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="طول بسته",
    )

    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="عرض بسته",
    )

    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="ارتفاع بسته",
    )

    # PackingId از:
    # /api/OM/v3/PackingPrices
    packing_id = models.PositiveIntegerField(
        default=0,
        verbose_name="Packing ID",
    )

    # packageContentId از:
    # /api/OM/v3/PackContentRates
    package_content_id = (
        models.PositiveIntegerField(
            verbose_name="Package Content ID",
        )
    )

    pack_type = models.PositiveSmallIntegerField(
        default=20,
        verbose_name="نوع بسته Tipax",
        help_text=(
            "شناسه نوع بسته در Tipax. "
            "برای بسته معمولی فروشگاه مقدار 20 استفاده می‌شود."
        ),
    )

    # از ParcelType/Search.
    parcel_type_id = models.PositiveIntegerField(
        default=0,
        verbose_name="Parcel Type ID",
    )

    is_unusual = models.BooleanField(
        default=False,
        verbose_name="بسته نامتعارف",
    )

    priority = models.IntegerField(
        default=0,
        verbose_name="اولویت",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:

        verbose_name = "پروفایل بسته تیپاکس"

        verbose_name_plural = (
            "پروفایل‌های بسته تیپاکس"
        )

        ordering = [
            "-priority",
            "min_weight_grams",
        ]

    def clean(self):

        super().clean()

        if (
            self.max_weight_grams is not None
            and
            self.max_weight_grams
            < self.min_weight_grams
        ):

            raise ValidationError(
                {
                    "max_weight_grams": (
                        "حداکثر وزن نمی‌تواند "
                        "کمتر از حداقل وزن باشد."
                    )
                }
            )

    def __str__(self):

        return self.title


# =========================================================
# Shipment
# =========================================================


class Shipment(models.Model):

    class Status(models.TextChoices):

        CREATED = (
            "created",
            "ایجاد شده",
        )

        REGISTERED = (
            "registered",
            "ثبت اولیه",
        )

        PROCESSING = (
            "processing",
            "در حال پردازش",
        )

        WAITING_PICKUP = (
            "waiting_pickup",
            "در انتظار جمع‌آوری",
        )

        COLLECTED = (
            "collected",
            "جمع‌آوری شده",
        )

        SHIPPED = (
            "shipped",
            "در حال ارسال",
        )

        DELIVERED = (
            "delivered",
            "تحویل شده",
        )

        RETURNED = (
            "returned",
            "عودت شده",
        )

        CANCELLED = (
            "cancelled",
            "ابطال شده",
        )


    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="shipments",
        verbose_name="سفارش",
    )

    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        related_name="shipments",
        null=True,
        blank=True,
        verbose_name="روش ارسال",
    )

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
        verbose_name="Provider",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
        verbose_name="وضعیت",
    )

    # orderId تیپاکس.
    external_order_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Order ID Provider",
    )

    # ممکن است Provider بیش از یک Tracking Code برگرداند.
    tracking_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="کدهای رهگیری",
    )

    primary_tracking_code = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="کد رهگیری اصلی",
    )

    provider_status_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد وضعیت Provider",
    )

    provider_status_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="وضعیت Provider",
    )

    quoted_amount_toman = (
        models.PositiveBigIntegerField(
            null=True,
            blank=True,
            verbose_name="هزینه برآوردشده",
        )
    )

    final_amount_toman = (
        models.PositiveBigIntegerField(
            null=True,
            blank=True,
            verbose_name="هزینه نهایی",
        )
    )

    request_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="درخواست Provider",
    )

    response_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="پاسخ Provider",
    )

    tracking_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="آخرین پاسخ رهگیری",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ابطال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        verbose_name = "مرسوله"
        verbose_name_plural = "مرسوله‌ها"

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return (
            f"{self.order.order_number} - "
            f"{self.provider}"
        )


# =========================================================
# Shipping Origin
# =========================================================


class ShippingOrigin(models.Model):
    """
    مبدا فیزیکی ارسال سفارش.

    مثال:
        انبار چابهار
        انبار تهران

    فقط یک مبدا می‌تواند Default باشد.

    تغییر مبدا Default فقط روی Quote و سفارش‌های جدید
    اثر می‌گذارد. سفارش‌های قبلی Snapshot خودشان را دارند.
    """

    title = models.CharField(
        max_length=120,
        verbose_name="عنوان مبدا",
    )

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="shipping_origins",
        verbose_name="استان",
    )

    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="shipping_origins",
        verbose_name="شهر",
    )

    postal_address = models.TextField(
        blank=True,
        default="",
        verbose_name="آدرس",
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="کد پستی",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="مبدا پیش‌فرض",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "مبدا ارسال"
        verbose_name_plural = "مبداهای ارسال"

        ordering = [
            "-is_default",
            "title",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "is_default",
                ],
                condition=models.Q(
                    is_default=True
                ),
                name=(
                    "shipping_single_default_origin"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.city.name}"
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.city_id
            and self.province_id
            and self.city.province_id
            != self.province_id
        ):
            errors["city"] = (
                "شهر انتخاب‌شده متعلق به استان انتخاب‌شده نیست."
            )

        if (
            self.is_default
            and not self.is_active
        ):
            errors["is_active"] = (
                "مبدا پیش‌فرض نمی‌تواند غیرفعال باشد."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def save(
            self,
            *args,
            **kwargs,
    ):

        with transaction.atomic():
            # اگر این Origin قرار است Default شود،
            # ابتدا Default قبلی را خاموش می‌کنیم.
            #
            # این کار داخل Transaction انجام می‌شود؛
            # بنابراین اگر validation یا save شکست بخورد،
            # تغییر Default قبلی نیز Rollback می‌شود.
            if self.is_default:
                (
                    ShippingOrigin.objects
                    .select_for_update()
                    .filter(
                        is_default=True,
                    )
                    .exclude(
                        pk=self.pk,
                    )
                    .update(
                        is_default=False,
                    )
                )

            # حالا Constraint دیگر دو Default نمی‌بیند.
            self.full_clean()

            return super().save(
                *args,
                **kwargs,
            )

    @classmethod
    def get_default(cls):
        return (
            cls.objects
            .select_related(
                "province",
                "city",
            )
            .filter(
                is_default=True,
                is_active=True,
            )
            .first()
        )

# =========================================================
# Provider Province Catalog
# =========================================================


class ShippingProviderProvince(models.Model):

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
    )

    provider_province_id = models.CharField(
        max_length=64,
        db_index=True,
    )

    name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_province_id",
                ],
                name=(
                    "shipping_unique_provider_province"
                ),
            ),
        ]

    def __str__(self):
        return (
            self.name
            or self.provider_province_id
        )


# =========================================================
# Provider City Catalog
# =========================================================


class ShippingProviderCity(models.Model):

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
    )

    provider_city_id = models.CharField(
        max_length=64,
        db_index=True,
    )

    provider_province_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
    )

    provider_uuid = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    latitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_city_id",
                ],
                name=(
                    "shipping_unique_provider_city"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.provider_city_id})"
        )


# =========================================================
# Provider Packing Option
# =========================================================


class ShippingProviderPackingOption(
    models.Model
):

    class Kind(models.TextChoices):

        CARTON = (
            "carton",
            "کارتن",
        )

        BUBBLE = (
            "bubble",
            "نایلون حبابدار",
        )

        ENVELOPE = (
            "envelope",
            "پاکت",
        )

        SACK = (
            "sack",
            "گونی",
        )

        FLYER = (
            "flyer",
            "فلایر",
        )

        NO_PACKING = (
            "no_packing",
            "بدون بسته‌بندی",
        )

        OTHER = (
            "other",
            "سایر",
        )

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
    )

    provider_packing_id = (
        models.PositiveBigIntegerField()
    )

    title = models.CharField(
        max_length=200,
    )

    kind = models.CharField(
        max_length=30,
        choices=Kind.choices,
        default=Kind.OTHER,
        db_index=True,
    )

    box_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    pack_type = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Physical dimensions
    # -------------------------

    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # -------------------------
    # Provider constraints
    # -------------------------

    min_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    min_length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    min_width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    min_height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    provider_price = models.DecimalField(
        max_digits=18,
        decimal_places=3,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "provider",
            "kind",
            "box_number",
            "provider_packing_id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_packing_id",
                ],
                name=(
                    "shipping_unique_provider_packing"
                ),
            ),
        ]

    @property
    def volume(self):

        if (
            self.length is None
            or self.width is None
            or self.height is None
        ):
            return None

        return (
            self.length
            * self.width
            * self.height
        )

    def __str__(self):
        return self.title

class ShippingProviderProvinceMap(models.Model):
    """
    اتصال Province داخلی پروژه به استان Provider.

    برای Tipax مقدار provider_province_id
    همان stateId برگشتی Cities API است.

    نام استان Provider را حدس نمی‌زنیم.
    """

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
    )

    province = models.ForeignKey(
        "addresses.Province",
        on_delete=models.CASCADE,
        related_name="shipping_provider_maps",
    )

    provider_province_id = models.CharField(
        max_length=64,
        db_index=True,
    )

    provider_province_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "province",
                ],
                name=(
                    "shipping_unique_provider_province_map"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "provider_province_id",
                ],
                name=(
                    "shipping_unique_provider_province_id_map"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.province.name} -> "
            f"{self.provider_province_id}"
        )

class ShippingProviderOriginMap(models.Model):

    provider = models.CharField(
        max_length=30,
        choices=ShippingMethod.Provider.choices,
        db_index=True,
        verbose_name="Provider",
    )

    origin = models.ForeignKey(
        ShippingOrigin,
        on_delete=models.CASCADE,
        related_name="provider_origin_maps",
        verbose_name="مبدا ارسال",
    )

    # همان originId مورد نیاز Tipax.
    provider_address_id = models.PositiveBigIntegerField(
        verbose_name="شناسه آدرس در Provider",
    )

    provider_address_title = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="عنوان آدرس در Provider",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات خام Provider",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        verbose_name = "اتصال مبدا به Provider"
        verbose_name_plural = "اتصال مبداها به Provider"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "provider",
                    "origin",
                ],
                name="shipping_unique_provider_origin_map",
            ),
        ]

    def __str__(self):

        return (
            f"{self.origin.title} → "
            f"{self.provider} "
            f"({self.provider_address_id})"
        )