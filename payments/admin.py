from django.contrib import admin

from .models import Payment

# =========================================================
# Payment Admin
# =========================================================


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "amount",
        "gateway",
        "status",
        "transaction_id",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "gateway",
        "created_at",
        "paid_at",
    )

    search_fields = (
        "order__id",
        "order__user__phone_number",
        "transaction_id",
        "authority",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "اطلاعات پرداخت",
            {
                "fields": (
                    "order",
                    "amount",
                    "gateway",
                    "status",
                )
            },
        ),
        (
            "اطلاعات درگاه",
            {
                "fields": (
                    "authority",
                    "transaction_id",
                    "paid_at",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
