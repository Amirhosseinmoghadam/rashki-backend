from django.contrib import (
    admin,
    messages,
)

from .models import (
    Order,
    OrderItem,
)

from .services import (
    InvalidOrderTransitionError,
    mark_order_delivered,
    mark_order_packing,
    mark_order_shipped,
)


# =========================================================
# Order Item Inline
# =========================================================


class OrderItemInline(
    admin.TabularInline
):

    model = OrderItem

    extra = 0

    can_delete = False

    fields = (
        "product_name",
        "product_sku",
        "unit_price_toman",
        "quantity",
        "total_price_toman",
    )

    readonly_fields = fields


# =========================================================
# Order Admin
# =========================================================


@admin.register(Order)
class OrderAdmin(
    admin.ModelAdmin
):

    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "formatted_total",
        "shipping_method_name",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "shipping_provider",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__phone_number",
        "shipping_mobile_number",
        "shipping_postal_code",
    )

    list_select_related = (
        "user",
        "shipping_method",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    inlines = (
        OrderItemInline,
    )

    actions = (
        "move_to_packing",
        "move_to_shipped",
        "move_to_delivered",
    )

    def get_readonly_fields(
        self,
        request,
        obj=None,
    ):

        return [
            field.name
            for field
            in self.model._meta.fields
        ]

    def has_add_permission(
        self,
        request,
    ):

        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):

        # سفارش‌های مالی حذف نمی‌شوند.
        return False

    @admin.display(
        description="مبلغ نهایی",
        ordering="total_toman",
    )
    def formatted_total(
        self,
        obj,
    ):

        return (
            f"{obj.total_toman:,} تومان"
        )

    def _apply_transition(
        self,
        request,
        queryset,
        function,
    ):

        success = 0
        failed = 0

        for order in queryset:

            try:

                function(
                    order
                )

                success += 1

            except (
                InvalidOrderTransitionError
            ):

                failed += 1

        self.message_user(
            request,
            (
                f"{success} سفارش بروزرسانی شد؛ "
                f"{failed} سفارش قابل تغییر نبود."
            ),
            level=(
                messages.SUCCESS
                if failed == 0
                else messages.WARNING
            ),
        )

    @admin.action(
        description="انتقال به در حال بسته‌بندی"
    )
    def move_to_packing(
        self,
        request,
        queryset,
    ):

        self._apply_transition(
            request,
            queryset,
            mark_order_packing,
        )

    @admin.action(
        description="ثبت به عنوان ارسال‌شده"
    )
    def move_to_shipped(
        self,
        request,
        queryset,
    ):

        self._apply_transition(
            request,
            queryset,
            mark_order_shipped,
        )

    @admin.action(
        description="ثبت به عنوان تحویل‌شده"
    )
    def move_to_delivered(
        self,
        request,
        queryset,
    ):

        self._apply_transition(
            request,
            queryset,
            mark_order_delivered,
        )