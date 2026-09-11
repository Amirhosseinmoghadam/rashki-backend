import uuid

from django.db import models
from django.db.models import Q


# =========================================================
# Payment Attempt
# =========================================================


class PaymentAttempt(models.Model):

    # =====================================================
    # Provider
    # =====================================================

    class Provider(models.TextChoices):

        # درگاه زرین‌پال.
        ZARINPAL = (
            "zarinpal",
            "زرین‌پال",
        )

        # سیستم تأیید کارت‌به‌کارت TCart.
        TCART = (
            "tcart",
            "TCart",
        )


    # =====================================================
    # Status
    # =====================================================

    class Status(models.TextChoices):

        # رکورد ساخته شده ولی هنوز Provider
        # پاسخ Start را نداده است.
        CREATED = (
            "created",
            "ایجاد شده",
        )

        # درخواست پرداخت با موفقیت در Provider
        # ساخته شده و منتظر پرداخت مشتری است.
        PENDING = (
            "pending",
            "در انتظار پرداخت",
        )

        # Provider پرداخت را Verify کرده است.
        SUCCEEDED = (
            "succeeded",
            "موفق",
        )

        # پرداخت یا Verify ناموفق شده است.
        FAILED = (
            "failed",
            "ناموفق",
        )

        # User در Provider پرداخت را لغو کرده است.
        CANCELLED = (
            "cancelled",
            "لغوشده",
        )

        # Attempt دیگر معتبر نیست.
        EXPIRED = (
            "expired",
            "منقضی",
        )


    # =====================================================
    # Public Identity
    # =====================================================

    # شناسه عمومی Attempt.
    #
    # در URL/API از UUID استفاده می‌کنیم
    # تا ID ترتیبی دیتابیس در معرض Client نباشد.
    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="شناسه عمومی",
    )

    # =====================================================
    # Order
    # =====================================================

    # سفارشی که این پرداخت برای آن ساخته شده است.
    #
    # Order مالی را با حذف Attempt نباید حذف کرد.
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="payment_attempts",
        verbose_name="سفارش",
    )

    # =====================================================
    # Provider
    # =====================================================

    # Provider انتخاب‌شده توسط User.
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        db_index=True,
        verbose_name="روش پرداخت",
    )

    # وضعیت Attempt.
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
        verbose_name="وضعیت پرداخت",
    )

    # =====================================================
    # Money
    # =====================================================

    # مبلغ اصلی سفارش در سیستم ما به تومان.
    #
    # این مقدار Snapshot است.
    amount_toman = models.PositiveBigIntegerField(
        verbose_name="مبلغ سفارش به تومان",
    )

    # مبلغی که واقعاً به Provider ارسال شده است.
    #
    # ممکن است:
    #
    # - با amount_toman برابر باشد.
    # - در Provider ریالی ×10 شده باشد.
    # - در TCart چند تومان Adjustment داشته باشد.
    provider_amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ Provider",
    )

    # واحد پول مبلغ Provider.
    #
    # مثال:
    # IRT
    # IRR
    provider_currency = models.CharField(
        max_length=10,
        verbose_name="واحد پول Provider",
    )

    # اختلاف مبلغ Provider با مبلغ اصلی به تومان.
    #
    # برای TCart ممکن است مثلاً:
    # +3 تومان
    #
    # باشد.
    #
    # این Adjustment نباید Order.total_toman
    # را تغییر دهد.
    provider_adjustment_toman = models.IntegerField(
        default=0,
        verbose_name="تعدیل مبلغ Provider به تومان",
    )

    # =====================================================
    # Provider References
    # =====================================================

    # شناسه اولیه‌ای که Provider ایجاد می‌کند.
    #
    # زرین‌پال:
    # Authority
    #
    # TCart:
    # Invoice ID
    provider_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شناسه Provider",
    )

    # شناسه نهایی تراکنش بعد از Verify.
    #
    # زرین‌پال:
    # ref_id
    provider_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شماره تراکنش Provider",
    )
    provider_session_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شناسه Session Provider",
    )

    # URLی که User برای پرداخت به آن هدایت می‌شود.
    gateway_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name="آدرس پرداخت",
    )

    # =====================================================
    # Idempotency
    # =====================================================

    # کلید یکتای Request پرداخت.
    #
    # تکرار Request با همین Key نباید
    # Attempt جدید ایجاد کند.
    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="کلید Idempotency",
    )

    # =====================================================
    # Audit Payloads
    # =====================================================

    # نسخه Sanitized درخواست Start.
    #
    # Secretها در این JSON ذخیره نمی‌شوند.
    request_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات درخواست",
    )

    # آخرین پاسخ Sanitized Provider.
    response_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="پاسخ Provider",
    )

    # اطلاعات Callback دریافت‌شده.
    callback_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات Callback",
    )

    # =====================================================
    # Error
    # =====================================================

    # کد خطای Provider.
    failure_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="کد خطا",
    )

    # متن خطای Provider.
    failure_message = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="پیام خطا",
    )

    # =====================================================
    # Dates
    # =====================================================

    # زمان موفقیت Start در Provider.
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان شروع پرداخت",
    )

    # مهلت Attempt.
    #
    # فعلاً با expires_at سفارش هماهنگ است.
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name="مهلت پرداخت",
    )

    # زمان Verify موفق.
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تایید پرداخت",
    )

    # زمان Failure.
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان شکست پرداخت",
    )

    # زمان ایجاد.
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ایجاد",
    )

    # زمان آخرین بروزرسانی.
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "تلاش پرداخت"

        verbose_name_plural = (
            "تلاش‌های پرداخت"
        )

        ordering = [
            "-created_at",
        ]

        indexes = [

            models.Index(
                fields=[
                    "order",
                    "status",
                ],
                name="payment_order_status_idx",
            ),

            models.Index(
                fields=[
                    "provider",
                    "provider_reference",
                ],
                name="payment_provider_ref_idx",
            ),
        ]

        constraints = [

            # هر Order فقط یک Payment موفق دارد.
            models.UniqueConstraint(
                fields=[
                    "order",
                ],
                condition=Q(
                    status="succeeded"
                ),
                name=(
                    "unique_successful_"
                    "payment_per_order"
                ),
            ),
        ]

    def __str__(self):

        return (
            f"{self.order.order_number} - "
            f"{self.provider} - "
            f"{self.status}"
        )



class PaymentRefund(models.Model):

    # =====================================================
    # Status
    # =====================================================

    class Status(models.TextChoices):

        # Refund در سیستم ما ساخته شده ولی هنوز
        # درخواست خارجی ارسال نشده است.
        CREATED = (
            "created",
            "ایجاد شده",
        )

        # درخواست Refund به Provider ارسال شده
        # ولی نتیجه نهایی هنوز قطعی نیست.
        PENDING = (
            "pending",
            "در انتظار نتیجه",
        )

        # Provider بازپرداخت را قطعی کرده است.
        SUCCEEDED = (
            "succeeded",
            "موفق",
        )

        # Provider به صورت قطعی Refund را رد کرده است.
        FAILED = (
            "failed",
            "ناموفق",
        )

        # وضعیت Provider نامشخص است؛ مثلاً Timeout
        # بعد از ارسال Request.
        #
        # در این حالت نباید دوباره کورکورانه
        # Refund انجام شود.
        REQUIRES_REVIEW = (
            "requires_review",
            "نیازمند بررسی",
        )

    # =====================================================
    # Public Identity
    # =====================================================

    public_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="شناسه عمومی بازپرداخت",
    )

    # =====================================================
    # Relations
    # =====================================================

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name="سفارش",
    )

    payment_attempt = models.ForeignKey(
        PaymentAttempt,
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name="پرداخت اصلی",
    )

    # =====================================================
    # Provider
    # =====================================================

    provider = models.CharField(
        max_length=30,
        choices=PaymentAttempt.Provider.choices,
        db_index=True,
        verbose_name="Provider پرداخت",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
        verbose_name="وضعیت بازپرداخت",
    )

    # =====================================================
    # Money
    # =====================================================

    # مبلغ Canonical سیستم ما همیشه تومان است.
    amount_toman = models.PositiveBigIntegerField(
        verbose_name="مبلغ بازپرداخت به تومان",
    )

    # تا زمانی که Contract دقیق Provider اعمال نشده،
    # این دو مقدار می‌توانند خالی باشند.
    provider_amount = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="مبلغ Provider",
    )

    provider_currency = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="واحد پول Provider",
    )

    # =====================================================
    # Provider References
    # =====================================================

    # برای زرین‌پال Refund به session_id نیاز داریم.
    #
    # برای Providerهای دیگر هم می‌توانیم شناسه مشابه
    # Provider را اینجا Snapshot کنیم.
    provider_session_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شناسه Session Provider",
    )

    # شناسه Refundی که Provider بعد از درخواست
    # بازمی‌گرداند.
    provider_refund_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="شناسه بازپرداخت Provider",
    )

    # =====================================================
    # Idempotency
    # =====================================================

    # یک درخواست Business یکسان نباید باعث
    # ایجاد چند Refund شود.
    idempotency_key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="کلید Idempotency",
    )

    # =====================================================
    # Business Information
    # =====================================================

    reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="دلیل بازپرداخت",
    )

    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="توضیحات بازپرداخت",
    )

    # =====================================================
    # Audit
    # =====================================================

    request_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="درخواست بازپرداخت",
    )

    response_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="پاسخ بازپرداخت",
    )

    # =====================================================
    # Error
    # =====================================================

    failure_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="کد خطا",
    )

    failure_message = models.CharField(
        max_length=1000,
        blank=True,
        verbose_name="پیام خطا",
    )

    # =====================================================
    # Dates
    # =====================================================

    requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال درخواست بازپرداخت",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تکمیل بازپرداخت",
    )

    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان شکست بازپرداخت",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:

        verbose_name = "بازپرداخت"

        verbose_name_plural = (
            "بازپرداخت‌ها"
        )

        ordering = [
            "-created_at",
        ]

        indexes = [

            models.Index(
                fields=[
                    "order",
                    "status",
                ],
                name="refund_order_status_idx",
            ),

            models.Index(
                fields=[
                    "payment_attempt",
                    "status",
                ],
                name="refund_attempt_status_idx",
            ),
        ]

        constraints = [

            models.CheckConstraint(
                condition=models.Q(
                    amount_toman__gt=0
                ),
                name="refund_amount_positive",
            ),
        ]

    def __str__(self):

        return (
            f"{self.order.order_number} - "
            f"{self.provider} - "
            f"{self.amount_toman} - "
            f"{self.status}"
        )