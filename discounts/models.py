# from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
#
#
# class Discount(models.Model):
#
#     class DiscountType(models.TextChoices):
#         PERCENTAGE = "percentage", "درصدی"
#         FIXED = "fixed", "مبلغ ثابت"
#
#     name = models.CharField(
#         max_length=200,
#         verbose_name="نام تخفیف",
#     )
#
#     discount_type = models.CharField(
#         max_length=20,
#         choices=DiscountType.choices,
#         verbose_name="نوع تخفیف",
#     )
#
#     value = models.DecimalField(
#         max_digits=15,
#         decimal_places=2,
#         validators=[
#             MinValueValidator(0),
#         ],
#         verbose_name="مقدار تخفیف",
#     )
#
#     products = models.ManyToManyField(
#         "products.Product",
#         blank=True,
#         related_name="discounts",
#         verbose_name="محصولات",
#     )
#
#     categories = models.ManyToManyField(
#         "categories.Category",
#         blank=True,
#         related_name="discounts",
#         verbose_name="دسته‌بندی‌ها",
#     )
#
#     starts_at = models.DateTimeField(
#         verbose_name="شروع",
#     )
#
#     ends_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name="پایان",
#     )
#
#     is_active = models.BooleanField(
#         default=True,
#         verbose_name="فعال",
#     )
#
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )
#
#     def __str__(self):
#         return self.name
#
#
# class Coupon(models.Model):
#
#     code = models.CharField(
#         max_length=50,
#         unique=True,
#         verbose_name="کد تخفیف",
#     )
#
#     discount_type = models.CharField(
#         max_length=20,
#         choices=Discount.DiscountType.choices,
#         verbose_name="نوع تخفیف",
#     )
#
#     value = models.DecimalField(
#         max_digits=15,
#         decimal_places=2,
#         validators=[
#             MinValueValidator(0),
#         ],
#         verbose_name="مقدار",
#     )
#
#     minimum_order_amount = models.DecimalField(
#         max_digits=15,
#         decimal_places=0,
#         null=True,
#         blank=True,
#         verbose_name="حداقل مبلغ سفارش",
#     )
#
#     maximum_discount_amount = models.DecimalField(
#         max_digits=15,
#         decimal_places=0,
#         null=True,
#         blank=True,
#         verbose_name="حداکثر مبلغ تخفیف",
#     )
#
#     usage_limit = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         verbose_name="محدودیت استفاده",
#     )
#
#     usage_limit_per_user = models.PositiveIntegerField(
#         default=1,
#         verbose_name="محدودیت استفاده برای هر کاربر",
#     )
#
#     starts_at = models.DateTimeField(
#         verbose_name="شروع",
#     )
#
#     ends_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name="پایان",
#     )
#
#     is_active = models.BooleanField(
#         default=True,
#         verbose_name="فعال",
#     )
#
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )
#
#     def __str__(self):
#         return self.code

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

from utils.normalizers import normalize_digits


# =========================================================
# Discount Code
# =========================================================


class DiscountCode(models.Model):

    # =====================================================
    # Choices
    # =====================================================

    class DiscountType(models.TextChoices):

        # تخفیف درصدی.
        # مثال: 20 درصد تخفیف.
        PERCENTAGE = (
            "percentage",
            "درصدی",
        )

        # تخفیف مبلغ ثابت به تومان.
        # مثال: 100,000 تومان تخفیف.
        FIXED_AMOUNT = (
            "fixed_amount",
            "مبلغ ثابت",
        )


    class Scope(models.TextChoices):

        # کد روی تمام محصولات سبد اعمال می‌شود.
        ALL = (
            "all",
            "تمام محصولات",
        )

        # کد فقط روی Productهای مشخص اعمال می‌شود.
        PRODUCTS = (
            "products",
            "محصولات مشخص",
        )

        # کد روی محصولات Categoryهای مشخص
        # و تمام زیرمجموعه‌های آن‌ها اعمال می‌شود.
        CATEGORIES = (
            "categories",
            "دسته‌بندی‌های مشخص",
        )


    # =====================================================
    # Main Information
    # =====================================================

    # کدی که کاربر در Checkout وارد می‌کند.
    #
    # مثال:
    # OFF20
    # RASHKI100
    #
    # هنگام ذخیره همیشه Uppercase می‌شود.
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تخفیف",
    )

    # توضیح داخلی برای Admin.
    #
    # مثال:
    # کمپین مهرماه برای کاربران سایت
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیحات",
    )

    # =====================================================
    # Discount Type
    # =====================================================

    # نوع تخفیف:
    # Percentage یا Fixed Amount.
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        verbose_name="نوع تخفیف",
    )

    # درصد تخفیف.
    #
    # فقط زمانی استفاده می‌شود که:
    # discount_type = percentage
    #
    # مثال:
    # 20
    # یعنی 20 درصد.
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.01")
            ),
            MaxValueValidator(
                Decimal("100")
            ),
        ],
        verbose_name="درصد تخفیف",
    )

    # مبلغ ثابت تخفیف به تومان.
    #
    # فقط زمانی استفاده می‌شود که:
    # discount_type = fixed_amount
    fixed_amount_toman = (
        models.PositiveBigIntegerField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(1),
            ],
            verbose_name=(
                "مبلغ ثابت تخفیف به تومان"
            ),
        )
    )

    # =====================================================
    # Discount Limits
    # =====================================================

    # حداقل مبلغ سبد خرید برای استفاده از کد.
    #
    # مبلغ قبل از تخفیف و بدون هزینه ارسال.
    #
    # مثال:
    # 1,000,000
    #
    # یعنی فقط سبدهای حداقل یک میلیون تومان.
    minimum_order_toman = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name=(
                "حداقل مبلغ سفارش به تومان"
            ),
        )
    )

    # سقف مبلغ تخفیف.
    #
    # بیشتر برای تخفیف درصدی استفاده می‌شود.
    #
    # مثال:
    # 20 درصد تخفیف
    # حداکثر 300,000 تومان
    maximum_discount_toman = (
        models.PositiveBigIntegerField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(1),
            ],
            verbose_name=(
                "حداکثر مبلغ تخفیف به تومان"
            ),
        )
    )

    # =====================================================
    # Scope
    # =====================================================

    # تعیین می‌کند کد روی چه Productهایی قابل استفاده است.
    scope = models.CharField(
        max_length=20,
        choices=Scope.choices,
        default=Scope.ALL,
        db_index=True,
        verbose_name="دامنه تخفیف",
    )

    # Productهایی که کد تخفیف روی آن‌ها قابل اعمال است.
    #
    # فقط برای:
    # scope = products
    products = models.ManyToManyField(
        "products.Product",
        related_name="discount_codes",
        blank=True,
        verbose_name="محصولات مشمول تخفیف",
    )

    # Categoryهایی که کد تخفیف روی آن‌ها اعمال می‌شود.
    #
    # محصولات زیرمجموعه Categoryها نیز مشمول هستند.
    categories = models.ManyToManyField(
        "categories.Category",
        related_name="discount_codes",
        blank=True,
        verbose_name="دسته‌بندی‌های مشمول تخفیف",
    )

    # =====================================================
    # Time
    # =====================================================

    # زمانی که کد از آن لحظه قابل استفاده است.
    start_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="زمان شروع",
    )

    # زمان انقضای کد.
    #
    # اگر خالی باشد کد تاریخ پایان ندارد.
    end_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="زمان پایان",
    )

    # =====================================================
    # Usage Limits
    # =====================================================

    # حداکثر تعداد استفاده از کد توسط تمام کاربران.
    #
    # اگر خالی باشد محدودیت کلی ندارد.
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="حداکثر تعداد استفاده",
    )

    # حداکثر دفعات استفاده هر کاربر.
    #
    # مثال:
    # 1
    #
    # یعنی هر User فقط یک‌بار.
    usage_limit_per_user = (
        models.PositiveIntegerField(
            null=True,
            blank=True,
            validators=[
                MinValueValidator(1),
            ],
            verbose_name=(
                "حداکثر استفاده هر کاربر"
            ),
        )
    )

    # =====================================================
    # Status
    # =====================================================

    # Admin می‌تواند بدون حذف کد،
    # آن را غیرفعال کند.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان ایجاد کد.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین بروزرسانی.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:

        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "is_active",
                    "start_at",
                    "end_at",
                ],
                name="discount_active_date_idx",
            ),
        ]

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):

        super().clean()

        errors = {}

        # ---------------------------------------------
        # Percentage
        # ---------------------------------------------

        if (
            self.discount_type
            == self.DiscountType.PERCENTAGE
        ):

            if self.percentage is None:

                errors[
                    "percentage"
                ] = (
                    "برای تخفیف درصدی "
                    "وارد کردن درصد الزامی است."
                )

        # ---------------------------------------------
        # Fixed Amount
        # ---------------------------------------------

        elif (
            self.discount_type
            == self.DiscountType.FIXED_AMOUNT
        ):

            if self.fixed_amount_toman is None:

                errors[
                    "fixed_amount_toman"
                ] = (
                    "برای تخفیف مبلغ ثابت "
                    "وارد کردن مبلغ الزامی است."
                )

        # ---------------------------------------------
        # Date
        # ---------------------------------------------

        if (
            self.end_at is not None
            and self.start_at is not None
            and self.end_at <= self.start_at
        ):

            errors[
                "end_at"
            ] = (
                "زمان پایان باید بعد از "
                "زمان شروع باشد."
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

        # اعداد فارسی/عربی به انگلیسی تبدیل می‌شوند.
        self.code = normalize_digits(
            self.code
        )

        # فاصله‌ها حذف و کد Uppercase می‌شود.
        self.code = (
            self.code
            .strip()
            .upper()
        )

        # فیلد نامرتبط با نوع تخفیف پاک می‌شود.
        if (
            self.discount_type
            == self.DiscountType.PERCENTAGE
        ):

            self.fixed_amount_toman = None

        elif (
            self.discount_type
            == self.DiscountType.FIXED_AMOUNT
        ):

            self.percentage = None

            self.maximum_discount_toman = None

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # String
    # =====================================================

    def __str__(self):

        return self.code


# =========================================================
# Discount Usage
# =========================================================


class DiscountUsage(models.Model):

    class Status(models.TextChoices):

        # کد با موفقیت برای سفارش مصرف شده است.
        USED = (
            "used",
            "استفاده شده",
        )

        # مصرف کد برگشت داده شده است.
        #
        # مثال:
        # Order لغو شده است.
        REVOKED = (
            "revoked",
            "برگشت داده شده",
        )

    # =====================================================
    # Discount
    # =====================================================

    # کد تخفیفی که استفاده شده است.
    #
    # PROTECT باعث می‌شود سابقه مالی حذف نشود.
    discount = models.ForeignKey(
        DiscountCode,
        on_delete=models.PROTECT,
        related_name="usages",
        verbose_name="کد تخفیف",
    )

    # =====================================================
    # User
    # =====================================================

    # کاربری که از کد استفاده کرده است.
    #
    # اگر User بعداً حذف شود، سابقه تخفیف باقی می‌ماند.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="discount_usages",
        null=True,
        blank=True,
        verbose_name="کاربر",
    )

    # =====================================================
    # Reference
    # =====================================================

    # شناسه یکتای مصرف کد.
    #
    # بعداً Order Number یا UUID سفارش در اینجا قرار می‌گیرد.
    #
    # مثال:
    # ORDER-2026-000128
    #
    # Unique بودن این فیلد مانع ثبت دوباره تخفیف
    # برای یک Order می‌شود.
    reference = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="مرجع استفاده",
    )

    # نسخه‌ای از Code هنگام مصرف.
    #
    # حتی اگر Code بعداً تغییر کند،
    # سابقه قبلی قابل مشاهده است.
    code_snapshot = models.CharField(
        max_length=50,
        verbose_name="نسخه کد تخفیف",
    )

    # =====================================================
    # Amount Snapshot
    # =====================================================

    # مبلغ کل کالاهای سفارش قبل از تخفیف
    # و بدون هزینه ارسال.
    subtotal_toman = (
        models.PositiveBigIntegerField(
            verbose_name=(
                "مبلغ سبد قبل از تخفیف"
            ),
        )
    )

    # مبلغ کالاهایی که واقعاً مشمول
    # این Discount بوده‌اند.
    eligible_subtotal_toman = (
        models.PositiveBigIntegerField(
            verbose_name=(
                "مبلغ مشمول تخفیف"
            ),
        )
    )

    # مبلغ واقعی تخفیفی که به Order داده شده است.
    discount_amount_toman = (
        models.PositiveBigIntegerField(
            verbose_name="مبلغ تخفیف",
        )
    )

    # =====================================================
    # Status
    # =====================================================

    # وضعیت مصرف.
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.USED,
        db_index=True,
        verbose_name="وضعیت",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان مصرف کد.
    used_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="زمان استفاده",
    )

    # اگر مصرف کد لغو شود،
    # زمان لغو در این فیلد ذخیره می‌شود.
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان برگشت",
    )

    class Meta:

        verbose_name = "استفاده از کد تخفیف"

        verbose_name_plural = (
            "استفاده‌های کد تخفیف"
        )

        ordering = [
            "-used_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "discount",
                    "status",
                    "-used_at",
                ],
                name="discount_usage_status_idx",
            ),

            models.Index(
                fields=[
                    "user",
                    "discount",
                    "status",
                ],
                name="discount_user_usage_idx",
            ),
        ]

    def __str__(self):

        return (
            f"{self.code_snapshot} - "
            f"{self.reference}"
        )