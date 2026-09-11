from django.conf import settings
from django.db import models
from django.db.models import Q


# =========================================================
# Order
# =========================================================


class Order(models.Model):

    # =====================================================
    # Order Status
    # =====================================================

    class Status(models.TextChoices):

        # سفارش ساخته شده و منتظر پرداخت است.
        PENDING_PAYMENT = (
            "pending_payment",
            "در انتظار پرداخت",
        )

        # پرداخت انجام شده و سفارش وارد فرایند شده است.
        PROCESSING = (
            "processing",
            "در حال پردازش",
        )

        # سفارش در حال بسته‌بندی است.
        PACKING = (
            "packing",
            "در حال بسته‌بندی",
        )

        # سفارش تحویل شرکت حمل‌ونقل شده است.
        SHIPPED = (
            "shipped",
            "ارسال شده",
        )

        # سفارش به مشتری تحویل شده است.
        DELIVERED = (
            "delivered",
            "تحویل شده",
        )

        # سفارش توسط کاربر یا Admin لغو شده است.
        CANCELLED = (
            "cancelled",
            "لغو شده",
        )

        # مهلت پرداخت سفارش تمام شده است.
        EXPIRED = (
            "expired",
            "منقضی شده",
        )


    # =====================================================
    # Payment Status
    # =====================================================

    class PaymentStatus(models.TextChoices):

        # هنوز پرداختی آغاز نشده است.
        UNPAID = (
            "unpaid",
            "پرداخت نشده",
        )

        # درخواست پرداخت ایجاد شده
        # ولی نتیجه نهایی هنوز مشخص نیست.
        PENDING = (
            "pending",
            "در انتظار نتیجه پرداخت",
        )

        # پرداخت با موفقیت Verify شده است.
        PAID = (
            "paid",
            "پرداخت شده",
        )

        # پرداخت ناموفق بوده است.
        FAILED = (
            "failed",
            "پرداخت ناموفق",
        )

        # مبلغ سفارش کامل Refund شده است.
        REFUNDED = (
            "refunded",
            "بازپرداخت کامل",
        )

        # بخشی از مبلغ Refund شده است.
        PARTIALLY_REFUNDED = (
            "partially_refunded",
            "بازپرداخت جزئی",
        )


    # =====================================================
    # Identity
    # =====================================================

    # شماره عمومی و یکتای سفارش.
    #
    # مثال:
    # RK-20260904-A84F123B
    order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="شماره سفارش",
    )

    # کاربری که Order را ثبت کرده است.
    #
    # Order مالی است و با حذف User
    # نباید حذف شود.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )

    # =====================================================
    # Status
    # =====================================================

    # وضعیت عملیاتی سفارش.
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
        verbose_name="وضعیت سفارش",
    )

    # وضعیت پرداخت مستقل از وضعیت Order.
    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    # =====================================================
    # Original Address
    # =====================================================

    # آدرس اصلی که هنگام Checkout انتخاب شده بود.
    #
    # Snapshot اصلی پایین ذخیره می‌شود،
    # بنابراین تغییر بعدی Address روی Order اثر ندارد.
    address = models.ForeignKey(
        "addresses.Address",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="آدرس اصلی",
    )

    # =====================================================
    # Address Snapshot
    # =====================================================

    # نام گیرنده هنگام ثبت سفارش.
    shipping_first_name = models.CharField(
        max_length=150,
        verbose_name="نام گیرنده",
    )

    # نام خانوادگی گیرنده.
    shipping_last_name = models.CharField(
        max_length=150,
        verbose_name="نام خانوادگی گیرنده",
    )

    # شماره موبایل گیرنده.
    shipping_mobile_number = models.CharField(
        max_length=20,
        verbose_name="موبایل گیرنده",
    )

    # شماره تلفن ثابت Snapshot شده.
    shipping_phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="تلفن گیرنده",
    )

    # نام استان در لحظه سفارش.
    shipping_province_name = models.CharField(
        max_length=150,
        verbose_name="استان",
    )

    # نام شهر در لحظه سفارش.
    shipping_city_name = models.CharField(
        max_length=150,
        verbose_name="شهر",
    )

    # کد پستی در لحظه سفارش.
    shipping_postal_code = models.CharField(
        max_length=20,
        verbose_name="کد پستی",
    )

    # آدرس کامل پستی.
    shipping_postal_address = models.TextField(
        verbose_name="آدرس پستی",
    )

    # =====================================================
    # Shipping
    # =====================================================

    # روش Shipping اصلی.
    #
    # Snapshotهای پایین اطلاعات تاریخی را حفظ می‌کنند.
    shipping_method = models.ForeignKey(
        "shipping.ShippingMethod",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="روش ارسال",
    )

    # کد روش ارسال Snapshot شده.
    shipping_method_code = models.CharField(
        max_length=100,
        verbose_name="کد روش ارسال",
    )

    # نام روش ارسال هنگام Checkout.
    shipping_method_name = models.CharField(
        max_length=150,
        verbose_name="نام روش ارسال",
    )

    # Provider هنگام سفارش.
    #
    # مثال:
    # post
    # tipax
    shipping_provider = models.CharField(
        max_length=50,
        verbose_name="شرکت حمل‌ونقل",
    )

    # کد سرویس Provider.
    shipping_service_code = models.CharField(
        max_length=100,
        verbose_name="کد سرویس ارسال",
    )

    # وزن نهایی مرسوله هنگام Checkout.
    shipping_weight_grams = (
        models.PositiveIntegerField(
            verbose_name="وزن مرسوله به گرم",
        )
    )

    # اطلاعات اضافی Provider/Rule.
    #
    # مثلاً:
    # rule_id
    # calculation mode
    shipping_provider_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات محاسبه ارسال",
    )

    # =====================================================
    # Discount
    # =====================================================

    # DiscountCode اصلی.
    #
    # حذف Discount نباید Order را حذف کند.
    discount = models.ForeignKey(
        "discounts.DiscountCode",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="کد تخفیف",
    )

    # کد تخفیف Snapshot شده.
    discount_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد تخفیف Snapshot",
    )

    # نوع تخفیف Snapshot شده.
    discount_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="نوع تخفیف",
    )

    # Scope تخفیف Snapshot شده.
    discount_scope = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="دامنه تخفیف",
    )

    # =====================================================
    # Amounts
    # =====================================================

    # مجموع قیمت تمام کالاها
    # قبل از Discount و Shipping.
    subtotal_toman = (
        models.PositiveBigIntegerField(
            verbose_name="جمع کالاها به تومان",
        )
    )

    # مبلغ کالاهایی که مشمول Discount بوده‌اند.
    eligible_discount_subtotal_toman = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name=(
                "جمع مبلغ مشمول تخفیف"
            ),
        )
    )

    # مبلغ واقعی Discount.
    discount_amount_toman = (
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="مبلغ تخفیف به تومان",
        )
    )

    # هزینه Shipping Snapshot شده.
    shipping_amount_toman = (
        models.PositiveBigIntegerField(
            verbose_name="هزینه ارسال به تومان",
        )
    )

    # مبلغ نهایی:
    #
    # subtotal
    # - discount
    # + shipping
    total_toman = (
        models.PositiveBigIntegerField(
            verbose_name="مبلغ نهایی به تومان",
        )
    )

    # =====================================================
    # Customer
    # =====================================================

    # توضیح اختیاری مشتری.
    customer_note = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="توضیحات مشتری",
    )

    # زمان قبول قوانین توسط User.
    terms_accepted_at = models.DateTimeField(
        verbose_name="زمان پذیرش قوانین",
    )

    # =====================================================
    # Stock Reservation
    # =====================================================

    # زمان رزرو/کسر موجودی.
    stock_reserved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان رزرو موجودی",
    )

    # اگر سفارش Cancel یا Expire شود،
    # موجودی فقط یک‌بار آزاد می‌شود.
    stock_released_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان آزادسازی موجودی",
    )

    # =====================================================
    # Payment Expiry
    # =====================================================

    # User تا این زمان فرصت پرداخت دارد.
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name="مهلت پرداخت",
    )

    # =====================================================
    # Operational Dates
    # =====================================================

    # زمان Verify شدن پرداخت.
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان پرداخت",
    )

    # زمان لغو Order.
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان لغو",
    )

    # زمان ارسال.
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال",
    )

    # زمان تحویل.
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تحویل",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان ایجاد Order.
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ثبت",
    )

    # آخرین تغییر.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

        ordering = [
            "-created_at",
        ]

        indexes = [

            models.Index(
                fields=[
                    "user",
                    "-created_at",
                ],
                name="order_user_date_idx",
            ),

            models.Index(
                fields=[
                    "status",
                    "payment_status",
                ],
                name="order_status_payment_idx",
            ),

            models.Index(
                fields=[
                    "status",
                    "expires_at",
                ],
                name="order_expiry_idx",
            ),
        ]

        constraints = [

            # Discount نمی‌تواند از Subtotal بیشتر باشد.
            models.CheckConstraint(
                condition=Q(
                    discount_amount_toman__lte=(
                        models.F(
                            "subtotal_toman"
                        )
                    )
                ),
                name=(
                    "order_discount_lte_subtotal"
                ),
            ),
        ]

    def __str__(self):

        return self.order_number


# =========================================================
# Order Item
# =========================================================


class OrderItem(models.Model):

    # =====================================================
    # Order
    # =====================================================

    # سفارشی که Item متعلق به آن است.
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )

    # =====================================================
    # Product
    # =====================================================

    # Product اصلی.
    #
    # PROTECT عمدی است.
    #
    # Productهایی که در Order استفاده شده‌اند
    # نباید فیزیکی Delete شوند؛ باید Archived شوند.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="محصول",
    )

    # ID Product نیز Snapshot می‌شود.
    product_id_snapshot = (
        models.PositiveBigIntegerField(
            verbose_name="شناسه محصول Snapshot",
        )
    )

    # نام Product هنگام Order.
    product_name = models.CharField(
        max_length=250,
        verbose_name="نام محصول",
    )

    # Slug هنگام سفارش.
    product_slug = models.CharField(
        max_length=280,
        blank=True,
        verbose_name="Slug محصول",
    )

    # SKU هنگام Order.
    product_sku = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="SKU",
    )

    # Brand هنگام سفارش.
    product_brand_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="برند محصول",
    )

    # واحد محصول.
    product_unit = models.CharField(
        max_length=30,
        verbose_name="واحد محصول",
    )

    # =====================================================
    # Price Snapshot
    # =====================================================

    # قیمت یک عدد Product در لحظه Order.
    unit_price_toman = (
        models.PositiveBigIntegerField(
            verbose_name="قیمت واحد به تومان",
        )
    )

    # تعداد خریداری‌شده.
    quantity = models.PositiveIntegerField(
        verbose_name="تعداد",
    )

    # قیمت کل Line.
    #
    # unit_price × quantity
    total_price_toman = (
        models.PositiveBigIntegerField(
            verbose_name="قیمت کل به تومان",
        )
    )

    class Meta:

        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

        ordering = [
            "id",
        ]

        constraints = [

            models.CheckConstraint(
                condition=Q(
                    quantity__gte=1
                ),
                name=(
                    "order_item_quantity_gte_1"
                ),
            ),
        ]

    def __str__(self):

        return (
            f"{self.product_name} × "
            f"{self.quantity}"
        )