from dataclasses import dataclass
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from django.db import transaction
from django.utils import timezone

from categories.models import Category

from products.models import Product

from .models import (
    DiscountCode,
    DiscountUsage,
)

from utils.normalizers import (
    normalize_digits,
)


# =========================================================
# Exceptions
# =========================================================


class DiscountError(Exception):
    pass


class DiscountValidationError(
    DiscountError
):
    pass


# =========================================================
# Line Item
# =========================================================


@dataclass
class DiscountLine:

    product: Product
    quantity: int
    unit_price_toman: int

    @property
    def product_id(self):
        return self.product.pk

    @property
    def total_toman(self):
        return (
            self.quantity
            * self.unit_price_toman
        )


# =========================================================
# Result
# =========================================================


@dataclass
class DiscountCalculationResult:

    discount: DiscountCode

    subtotal_toman: int

    eligible_subtotal_toman: int

    discount_amount_toman: int

    final_subtotal_toman: int


# =========================================================
# Normalize Code
# =========================================================


def normalize_discount_code(
    code,
):

    code = normalize_digits(
        code
    )

    return (
        str(code)
        .strip()
        .upper()
    )


# =========================================================
# Get Discount
# =========================================================


def get_discount_by_code(
    code,
):

    code = normalize_discount_code(
        code
    )

    discount = (
        DiscountCode.objects
        .filter(
            code=code
        )
        .first()
    )

    if discount is None:

        raise DiscountValidationError(
            "کد تخفیف معتبر نیست."
        )

    return discount


# =========================================================
# Descendant Categories
# =========================================================


def get_category_descendant_ids(
    root_ids,
):

    root_ids = set(
        root_ids
    )

    categories = list(
        Category.objects.all().only(
            "id",
            "parent_id",
        )
    )

    children_map = {}

    for category in categories:

        children_map.setdefault(
            category.parent_id,
            [],
        ).append(
            category.id
        )

    result = set()

    stack = list(
        root_ids
    )

    while stack:

        category_id = stack.pop()

        if category_id in result:
            continue

        result.add(
            category_id
        )

        stack.extend(
            children_map.get(
                category_id,
                [],
            )
        )

    return result


# =========================================================
# Usage Validation
# =========================================================


def validate_usage_limits(
    discount,
    user,
):

    active_usages = (
        discount.usages.filter(
            status=(
                DiscountUsage.Status.USED
            )
        )
    )

    # ---------------------------------------------
    # Global Limit
    # ---------------------------------------------

    if (
        discount.usage_limit
        is not None
        and active_usages.count()
        >= discount.usage_limit
    ):

        raise DiscountValidationError(
            "ظرفیت استفاده از این "
            "کد تخفیف به پایان رسیده است."
        )

    # ---------------------------------------------
    # User Limit
    # ---------------------------------------------

    if (
        discount.usage_limit_per_user
        is not None
    ):

        if user is None:

            raise DiscountValidationError(
                "برای استفاده از این "
                "کد باید وارد حساب خود شوید."
            )

        user_count = (
            active_usages.filter(
                user=user
            ).count()
        )

        if (
            user_count
            >= discount.usage_limit_per_user
        ):

            raise DiscountValidationError(
                "شما به حداکثر تعداد "
                "استفاده از این کد رسیده‌اید."
            )


# =========================================================
# Calculate Discount
# =========================================================


def calculate_discount(
    *,
    discount,
    lines,
    user=None,
    at=None,
):

    at = at or timezone.now()

    # =====================================================
    # Basic Validation
    # =====================================================

    if not discount.is_active:

        raise DiscountValidationError(
            "این کد تخفیف غیرفعال است."
        )

    if at < discount.start_at:

        raise DiscountValidationError(
            "زمان استفاده از این "
            "کد تخفیف هنوز شروع نشده است."
        )

    if (
        discount.end_at is not None
        and at > discount.end_at
    ):

        raise DiscountValidationError(
            "این کد تخفیف منقضی شده است."
        )

    validate_usage_limits(
        discount,
        user,
    )

    # =====================================================
    # Subtotal
    # =====================================================

    subtotal_toman = sum(
        line.total_toman
        for line in lines
    )

    if subtotal_toman <= 0:

        raise DiscountValidationError(
            "سبد خرید خالی است."
        )

    # حداقل خرید بر اساس مبلغ کل کالاها
    # قبل از Discount و Shipping است.
    if (
        subtotal_toman
        < discount.minimum_order_toman
    ):

        raise DiscountValidationError(
            (
                "حداقل مبلغ سفارش برای "
                f"استفاده از این کد "
                f"{discount.minimum_order_toman:,} "
                "تومان است."
            )
        )

    # =====================================================
    # Eligible Products
    # =====================================================

    if (
        discount.scope
        == DiscountCode.Scope.ALL
    ):

        eligible_subtotal = (
            subtotal_toman
        )

    elif (
        discount.scope
        == DiscountCode.Scope.PRODUCTS
    ):

        product_ids = set(
            discount.products
            .values_list(
                "id",
                flat=True,
            )
        )

        eligible_subtotal = sum(
            line.total_toman
            for line in lines
            if line.product_id
            in product_ids
        )

    elif (
        discount.scope
        == DiscountCode.Scope.CATEGORIES
    ):

        root_category_ids = (
            discount.categories
            .values_list(
                "id",
                flat=True,
            )
        )

        category_ids = (
            get_category_descendant_ids(
                root_category_ids
            )
        )

        eligible_subtotal = sum(
            line.total_toman
            for line in lines
            if (
                line.product.category_id
                in category_ids
            )
        )

    else:

        raise DiscountValidationError(
            "دامنه کد تخفیف نامعتبر است."
        )

    if eligible_subtotal <= 0:

        raise DiscountValidationError(
            "هیچ‌یک از محصولات سبد "
            "مشمول این کد تخفیف نیستند."
        )

    # =====================================================
    # Percentage
    # =====================================================

    if (
        discount.discount_type
        == DiscountCode
        .DiscountType
        .PERCENTAGE
    ):

        amount = (
            Decimal(
                eligible_subtotal
            )
            *
            discount.percentage
            /
            Decimal("100")
        )

        amount = int(
            amount.quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

        # سقف Discount.
        if (
            discount.maximum_discount_toman
            is not None
        ):

            amount = min(
                amount,
                discount.maximum_discount_toman,
            )

    # =====================================================
    # Fixed Amount
    # =====================================================

    elif (
        discount.discount_type
        == DiscountCode
        .DiscountType
        .FIXED_AMOUNT
    ):

        amount = (
            discount.fixed_amount_toman
        )

    else:

        raise DiscountValidationError(
            "نوع کد تخفیف نامعتبر است."
        )

    # تخفیف هیچ‌وقت بیشتر از مبلغ
    # محصولات مشمول نمی‌شود.
    amount = min(
        amount,
        eligible_subtotal,
    )

    final_subtotal = (
        subtotal_toman
        - amount
    )

    return DiscountCalculationResult(
        discount=discount,
        subtotal_toman=subtotal_toman,
        eligible_subtotal_toman=(
            eligible_subtotal
        ),
        discount_amount_toman=amount,
        final_subtotal_toman=(
            final_subtotal
        ),
    )


# =========================================================
# Consume Discount
# =========================================================


@transaction.atomic
def consume_discount(
    *,
    discount,
    user,
    lines,
    reference,
):

    reference = str(
        reference
    ).strip()

    if not reference:

        raise DiscountValidationError(
            "مرجع استفاده از کد الزامی است."
        )

    # اگر قبلاً همین Order ثبت شده باشد،
    # دوباره Usage ایجاد نمی‌کنیم.
    existing = (
        DiscountUsage.objects
        .filter(
            reference=reference
        )
        .first()
    )

    if existing is not None:

        if (
            existing.discount_id
            != discount.id
        ):

            raise DiscountValidationError(
                "این مرجع قبلاً برای "
                "کد دیگری استفاده شده است."
            )

        return existing

    # Lock روی Discount باعث می‌شود دو Checkout
    # همزمان نتوانند آخرین ظرفیت Code را مصرف کنند.
    discount = (
        DiscountCode.objects
        .select_for_update()
        .get(
            pk=discount.pk
        )
    )

    result = calculate_discount(
        discount=discount,
        lines=lines,
        user=user,
    )

    usage = DiscountUsage.objects.create(
        discount=discount,
        user=user,
        reference=reference,
        code_snapshot=(
            discount.code
        ),
        subtotal_toman=(
            result.subtotal_toman
        ),
        eligible_subtotal_toman=(
            result
            .eligible_subtotal_toman
        ),
        discount_amount_toman=(
            result.discount_amount_toman
        ),
        status=(
            DiscountUsage.Status.USED
        ),
    )

    return usage


# =========================================================
# Revoke Usage
# =========================================================


@transaction.atomic
def revoke_discount_usage(
    reference,
):

    usage = (
        DiscountUsage.objects
        .select_for_update()
        .filter(
            reference=reference
        )
        .first()
    )

    if usage is None:

        raise DiscountValidationError(
            "سابقه استفاده از کد "
            "پیدا نشد."
        )

    if (
        usage.status
        == DiscountUsage.Status.REVOKED
    ):

        return usage

    usage.status = (
        DiscountUsage.Status.REVOKED
    )

    usage.revoked_at = (
        timezone.now()
    )

    usage.save(
        update_fields=[
            "status",
            "revoked_at",
        ]
    )

    return usage