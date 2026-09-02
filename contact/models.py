from django.core.validators import RegexValidator
from django.db import models


# =========================================================
# Contact Request
# =========================================================


class ContactRequest(models.Model):

    # =====================================================
    # Subject
    # =====================================================

    class Subject(models.TextChoices):

        WHOLESALE_COOPERATION = (
            "wholesale_cooperation",
            "درخواست همکاری عمده",
        )

        PRICE_INQUIRY = (
            "price_inquiry",
            "استعلام قیمت",
        )

        AVAILABILITY_INQUIRY = (
            "availability_inquiry",
            "استعلام موجودی",
        )

        PRODUCT_QUESTION = (
            "product_question",
            "پرسش درباره محصول",
        )

        OTHER = (
            "other",
            "سایر",
        )

    # =====================================================
    # Validators
    # =====================================================

    phone_validator = RegexValidator(
        regex=r"^09\d{9}$",
        message=(
            "شماره تماس باید به صورت "
            "09123456789 باشد."
        ),
    )

    # =====================================================
    # Customer
    # =====================================================

    first_name = models.CharField(
        max_length=100,
        verbose_name="نام",
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name="نام خانوادگی",
    )

    phone_number = models.CharField(
        max_length=11,
        validators=[
            phone_validator,
        ],
        verbose_name="شماره تماس",
    )

    # =====================================================
    # Request
    # =====================================================

    subject = models.CharField(
        max_length=50,
        choices=Subject.choices,
        verbose_name="موضوع درخواست",
    )

    description = models.TextField(
        max_length=3000,
        verbose_name="توضیحات",
    )

    # =====================================================
    # Status
    # =====================================================

    is_read = models.BooleanField(
        default=False,
        verbose_name="خوانده شده",
    )

    # =====================================================
    # Dates
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="تاریخ ثبت",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    # =====================================================
    # Meta
    # =====================================================

    class Meta:

        verbose_name = "درخواست تماس"

        verbose_name_plural = (
            "درخواست‌های تماس"
        )

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "phone_number",
                    "-created_at",
                ],
                name=(
                    "contact_phone_created_idx"
                ),
            ),
            models.Index(
                fields=[
                    "subject",
                    "-created_at",
                ],
                name=(
                    "contact_subject_created_idx"
                ),
            ),
            models.Index(
                fields=[
                    "is_read",
                    "-created_at",
                ],
                name=(
                    "contact_read_created_idx"
                ),
            ),
        ]

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        return (
            f"{self.first_name} "
            f"{self.last_name} - "
            f"{self.get_subject_display()}"
        )