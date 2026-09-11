from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone


# =========================================================
# Exchange Rate
# =========================================================


class ExchangeRate(models.Model):

    # =====================================================
    # Currency
    # =====================================================

    # کد ارز.
    # فعلاً USD استفاده می‌کنیم، ولی ساختار طوری است
    # که بعداً EUR یا ارزهای دیگر هم قابل اضافه شدن باشند.
    #
    # مثال:
    # USD
    # EUR
    currency = models.CharField(
        max_length=3,
        default="USD",
        db_index=True,
        verbose_name="ارز",
    )

    # =====================================================
    # Rate
    # =====================================================

    # ارزش یک واحد ارز به تومان.
    #
    # مثال:
    # اگر هر دلار 105,000 تومان باشد:
    #
    # rate_toman = 105000
    rate_toman = models.PositiveBigIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="نرخ به تومان",
    )

    # =====================================================
    # Active
    # =====================================================

    # مشخص می‌کند این Rate نرخ فعلی سیستم است یا خیر.
    #
    # برای هر ارز فقط یک ExchangeRate
    # می‌تواند Active باشد.
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="نرخ فعال",
    )

    # =====================================================
    # Effective Time
    # =====================================================

    # زمانی که این نرخ از نظر کسب‌وکار معتبر شده است.
    #
    # معمولاً هنگام ثبت نرخ جدید همان زمان فعلی است،
    # ولی می‌توانیم در Admin زمان دیگری هم تعیین کنیم.
    effective_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="زمان اعمال نرخ",
    )

    # =====================================================
    # Note
    # =====================================================

    # توضیح اختیاری برای نرخ.
    #
    # مثال:
    # نرخ بازار آزاد - ۱۴ شهریور
    note = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="یادداشت",
    )

    # =====================================================
    # User
    # =====================================================

    # ادمینی که این نرخ را ثبت کرده است.
    #
    # برای Audit و بررسی تغییرات قیمت در آینده مفید است.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_exchange_rates",
        null=True,
        blank=True,
        editable=False,
        verbose_name="ثبت‌کننده",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان ایجاد رکورد نرخ ارز.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین تغییر رکورد.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:

        verbose_name = "نرخ ارز"
        verbose_name_plural = "نرخ‌های ارز"

        ordering = [
            "-effective_at",
            "-created_at",
        ]

        constraints = [

            # برای هر ارز فقط یک Rate فعال
            # در دیتابیس وجود خواهد داشت.
            models.UniqueConstraint(
                fields=[
                    "currency",
                ],
                condition=Q(
                    is_active=True
                ),
                name=(
                    "unique_active_exchange_"
                    "rate_per_currency"
                ),
            ),
        ]

        indexes = [

            # برای پیدا کردن سریع تاریخچه نرخ یک ارز.
            models.Index(
                fields=[
                    "currency",
                    "-effective_at",
                ],
                name="exchange_currency_date_idx",
            ),
        ]

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        # کد ارز همیشه با حروف بزرگ ذخیره می‌شود.
        #
        # usd
        # تبدیل می‌شود به:
        # USD
        self.currency = (
            self.currency
            .strip()
            .upper()
        )

        # اگر این Rate فعال شده باشد،
        # تمام Rateهای فعال قبلی همین ارز
        # غیرفعال می‌شوند.
        with transaction.atomic():

            if self.is_active:

                (
                    ExchangeRate.objects
                    .filter(
                        currency=self.currency,
                        is_active=True,
                    )
                    .exclude(
                        pk=self.pk
                    )
                    .update(
                        is_active=False
                    )
                )

            super().save(
                *args,
                **kwargs,
            )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        return (
            f"{self.currency} - "
            f"{self.rate_toman:,} تومان"
        )


# =========================================================
# Pricing Settings
# =========================================================


class PricingSettings(models.Model):

    class RoundingMode(
        models.TextChoices
    ):

        # قیمت به نزدیک‌ترین Step گرد می‌شود.
        #
        # مثال با Step = 10,000:
        # 1,234,000 → 1,230,000
        # 1,236,000 → 1,240,000
        NEAREST = (
            "nearest",
            "نزدیک‌ترین مقدار",
        )

        # قیمت همیشه رو به بالا گرد می‌شود.
        #
        # مثال:
        # 1,231,000 → 1,240,000
        UP = (
            "up",
            "رو به بالا",
        )

        # قیمت همیشه رو به پایین گرد می‌شود.
        #
        # مثال:
        # 1,239,000 → 1,230,000
        DOWN = (
            "down",
            "رو به پایین",
        )

    # =====================================================
    # Rounding
    # =====================================================

    # قیمت نهایی مضربی از این عدد خواهد شد.
    #
    # مثال:
    # 1000
    # یعنی قیمت‌ها به نزدیک‌ترین 1000 تومان
    # گرد شوند.
    #
    # اگر:
    # 10000
    # باشد، قیمت‌ها مضرب 10,000 تومان می‌شوند.
    rounding_step_toman = (
        models.PositiveIntegerField(
            default=1000,
            validators=[
                MinValueValidator(1),
            ],
            verbose_name=(
                "گام گردکردن قیمت به تومان"
            ),
        )
    )

    # روش گردکردن قیمت.
    rounding_mode = models.CharField(
        max_length=20,
        choices=RoundingMode.choices,
        default=RoundingMode.NEAREST,
        verbose_name="روش گردکردن قیمت",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان آخرین تغییر تنظیمات قیمت.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:

        verbose_name = "تنظیمات قیمت‌گذاری"

        verbose_name_plural = (
            "تنظیمات قیمت‌گذاری"
        )

    # =====================================================
    # Singleton
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        # این Model باید فقط یک رکورد داشته باشد.
        #
        # بنابراین PK همیشه 1 است.
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

        # تنظیمات اصلی Pricing نباید حذف شوند.
        pass

    @classmethod
    def load(cls):

        # تنظیمات را دریافت می‌کند.
        #
        # اگر هنوز وجود نداشته باشد،
        # اولین رکورد با تنظیمات Default ساخته می‌شود.
        obj, _ = cls.objects.get_or_create(
            pk=1
        )

        return obj

    def __str__(self):

        return "تنظیمات قیمت‌گذاری"