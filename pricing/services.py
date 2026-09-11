from dataclasses import dataclass
from decimal import (
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_UP,
)

from django.db import transaction
from django.utils import timezone

from products.models import Product

from .models import (
    ExchangeRate,
    PricingSettings,
)


# =========================================================
# Exceptions
# =========================================================


class PricingError(Exception):
    """
    خطای عمومی سیستم قیمت‌گذاری.
    """

    pass


class ExchangeRateNotFoundError(
    PricingError
):
    """
    زمانی استفاده می‌شود که نرخ فعال
    برای ارز موردنظر پیدا نشود.
    """

    pass


class InvalidProductPriceError(
    PricingError
):
    """
    زمانی استفاده می‌شود که اطلاعات قیمت
    محصول ناقص یا نامعتبر باشد.
    """

    pass


# =========================================================
# Price Result
# =========================================================


@dataclass
class PriceCalculationResult:

    # قیمت پایه قبل از Markup
    # و هزینه ثابت.
    base_price_toman: int

    # مبلغی که به دلیل markup_percent
    # به قیمت اضافه شده است.
    markup_amount_toman: int

    # هزینه ثابت محصول.
    fixed_cost_toman: int

    # قیمت قبل از گردکردن.
    raw_price_toman: int

    # قیمت نهایی پس از گردکردن.
    final_price_toman: int

    # نرخ دلار استفاده‌شده.
    #
    # برای محصولات Fixed مقدار None دارد.
    exchange_rate_toman: int | None


# =========================================================
# Exchange Rate
# =========================================================


def get_active_exchange_rate(
    currency="USD",
):

    # کد ارز استاندارد می‌شود.
    currency = (
        currency
        .strip()
        .upper()
    )

    # نرخ فعال ارز را دریافت می‌کنیم.
    exchange_rate = (
        ExchangeRate.objects
        .filter(
            currency=currency,
            is_active=True,
        )
        .first()
    )

    # اگر نرخ فعالی وجود نداشت،
    # محاسبه قیمت دلاری امکان‌پذیر نیست.
    if exchange_rate is None:

        raise ExchangeRateNotFoundError(
            f"نرخ فعال برای ارز "
            f"{currency} تعریف نشده است."
        )

    return exchange_rate


# =========================================================
# Rounding
# =========================================================


def round_toman(
    amount,
    step,
    mode,
):

    # تمام محاسبات با Decimal انجام می‌شود
    # تا مشکل Floating Point نداشته باشیم.
    amount = Decimal(
        str(amount)
    )

    step = Decimal(
        str(step)
    )

    if step <= 0:

        raise PricingError(
            "گام گردکردن قیمت "
            "باید بزرگ‌تر از صفر باشد."
        )

    # مشخص می‌کنیم مقدار چند Step دارد.
    units = (
        amount
        / step
    )

    # ---------------------------------------------
    # Nearest
    # ---------------------------------------------

    if (
        mode
        == PricingSettings
        .RoundingMode
        .NEAREST
    ):

        rounded_units = units.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )

    # ---------------------------------------------
    # Up
    # ---------------------------------------------

    elif (
        mode
        == PricingSettings
        .RoundingMode
        .UP
    ):

        rounded_units = units.quantize(
            Decimal("1"),
            rounding=ROUND_CEILING,
        )

    # ---------------------------------------------
    # Down
    # ---------------------------------------------

    elif (
        mode
        == PricingSettings
        .RoundingMode
        .DOWN
    ):

        rounded_units = units.quantize(
            Decimal("1"),
            rounding=ROUND_FLOOR,
        )

    else:

        raise PricingError(
            "روش گردکردن قیمت "
            "نامعتبر است."
        )

    return int(
        rounded_units
        * step
    )


# =========================================================
# Calculate Product Price
# =========================================================


def calculate_product_price(
    product,
    exchange_rate=None,
    pricing_settings=None,
):

    # تنظیمات Pricing را دریافت می‌کنیم.
    if pricing_settings is None:

        pricing_settings = (
            PricingSettings.load()
        )

    # =====================================================
    # USD Based
    # =====================================================

    if (
        product.pricing_mode
        == Product.PricingMode.USD_BASED
    ):

        # محصول دلاری باید قیمت پایه دلار داشته باشد.
        if product.base_price_usd is None:

            raise InvalidProductPriceError(
                "قیمت پایه دلاری محصول "
                "تعریف نشده است."
            )

        # اگر Rate از بیرون ارسال نشده باشد،
        # نرخ فعال USD دریافت می‌شود.
        if exchange_rate is None:

            exchange_rate = (
                get_active_exchange_rate(
                    "USD"
                )
            )

        # قیمت پایه به تومان:
        #
        # قیمت دلار محصول
        # ×
        # نرخ یک دلار به تومان
        base_price_toman = (
            Decimal(
                str(
                    product.base_price_usd
                )
            )
            *
            Decimal(
                str(
                    exchange_rate
                    .rate_toman
                )
            )
        )

        exchange_rate_toman = (
            exchange_rate.rate_toman
        )

    # =====================================================
    # Fixed Toman
    # =====================================================

    elif (
        product.pricing_mode
        == Product.PricingMode.FIXED
    ):

        # محصول ثابت باید قیمت پایه تومان داشته باشد.
        if product.base_price_toman is None:

            raise InvalidProductPriceError(
                "قیمت پایه تومان محصول "
                "تعریف نشده است."
            )

        base_price_toman = Decimal(
            str(
                product.base_price_toman
            )
        )

        # محصول Fixed از نرخ دلار استفاده نمی‌کند.
        exchange_rate_toman = None

    else:

        raise InvalidProductPriceError(
            "روش قیمت‌گذاری محصول "
            "نامعتبر است."
        )

    # =====================================================
    # Markup
    # =====================================================

    # درصد افزایش قیمت محصول.
    markup_percent = Decimal(
        str(
            product.markup_percent
        )
    )

    # مبلغ افزایش قیمت.
    #
    # مثال:
    #
    # Base:
    # 1,000,000
    #
    # Markup:
    # 20%
    #
    # Markup Amount:
    # 200,000
    markup_amount = (
        base_price_toman
        *
        markup_percent
        /
        Decimal("100")
    )

    # =====================================================
    # Fixed Cost
    # =====================================================

    # هزینه ثابت محصول.
    fixed_cost = Decimal(
        str(
            product.fixed_cost_toman
            or 0
        )
    )

    # =====================================================
    # Raw Price
    # =====================================================

    # قیمت قبل از گردکردن.
    raw_price = (
        base_price_toman
        +
        markup_amount
        +
        fixed_cost
    )

    if raw_price <= 0:

        raise InvalidProductPriceError(
            "قیمت محاسبه‌شده محصول "
            "باید بزرگ‌تر از صفر باشد."
        )

    # =====================================================
    # Final Price
    # =====================================================

    # قیمت بر اساس تنظیمات سیستم
    # گرد می‌شود.
    final_price = round_toman(
        amount=raw_price,
        step=(
            pricing_settings
            .rounding_step_toman
        ),
        mode=(
            pricing_settings
            .rounding_mode
        ),
    )

    # نتیجه کامل را برمی‌گردانیم.
    return PriceCalculationResult(

        base_price_toman=int(
            base_price_toman
        ),

        markup_amount_toman=int(
            markup_amount
        ),

        fixed_cost_toman=int(
            fixed_cost
        ),

        raw_price_toman=int(
            raw_price
        ),

        final_price_toman=(
            final_price
        ),

        exchange_rate_toman=(
            exchange_rate_toman
        ),
    )


# =========================================================
# Recalculate One Product
# =========================================================


def recalculate_product_price(
    product,
    *,
    exchange_rate=None,
    force=False,
):

    # اگر قیمت Product قفل شده باشد،
    # Rate جدید نباید قیمت آن را تغییر دهد.
    if (
        product.is_price_locked
        and not force
    ):

        return None

    result = calculate_product_price(
        product=product,
        exchange_rate=exchange_rate,
    )

    now = timezone.now()

    # مقدار Object داخل حافظه را نیز
    # بروزرسانی می‌کنیم.
    product.current_price_toman = (
        result.final_price_toman
    )

    product.last_exchange_rate_toman = (
        result.exchange_rate_toman
    )

    product.price_updated_at = now

    # از update استفاده می‌کنیم
    # تا Product.save دوباره اجرا نشود.
    Product.objects.filter(
        pk=product.pk
    ).update(
        current_price_toman=(
            result.final_price_toman
        ),
        last_exchange_rate_toman=(
            result.exchange_rate_toman
        ),
        price_updated_at=now,
    )

    return result


# =========================================================
# Recalculate USD Products
# =========================================================


@transaction.atomic
def recalculate_usd_products(
    *,
    exchange_rate=None,
    batch_size=1000,
):

    # اگر Rate مشخص نشده باشد،
    # Rate فعال USD استفاده می‌شود.
    if exchange_rate is None:

        exchange_rate = (
            get_active_exchange_rate(
                "USD"
            )
        )

    pricing_settings = (
        PricingSettings.load()
    )

    # فقط Productهای دلاری:
    #
    # - آرشیوشده نیستند
    # - قیمتشان قفل نشده است
    queryset = (
        Product.objects
        .filter(
            pricing_mode=(
                Product
                .PricingMode
                .USD_BASED
            ),
            is_price_locked=False,
        )
        .exclude(
            status=(
                Product
                .Status
                .ARCHIVED
            )
        )
        .order_by(
            "pk"
        )
    )

    now = timezone.now()

    updated_count = 0

    batch = []

    # iterator باعث می‌شود برای تعداد بالای Product
    # همه رکوردها یک‌جا داخل RAM قرار نگیرند.
    for product in queryset.iterator(
        chunk_size=batch_size
    ):

        result = calculate_product_price(
            product=product,
            exchange_rate=exchange_rate,
            pricing_settings=(
                pricing_settings
            ),
        )

        product.current_price_toman = (
            result.final_price_toman
        )

        product.last_exchange_rate_toman = (
            exchange_rate.rate_toman
        )

        product.price_updated_at = now

        batch.append(
            product
        )

        # وقتی Batch پر شد
        # یک Bulk Update انجام می‌شود.
        if len(batch) >= batch_size:

            Product.objects.bulk_update(
                batch,
                fields=[
                    "current_price_toman",
                    "last_exchange_rate_toman",
                    "price_updated_at",
                ],
                batch_size=batch_size,
            )

            updated_count += len(
                batch
            )

            batch.clear()

    # آخرین Batch که ممکن است کمتر از
    # batch_size باشد.
    if batch:

        Product.objects.bulk_update(
            batch,
            fields=[
                "current_price_toman",
                "last_exchange_rate_toman",
                "price_updated_at",
            ],
            batch_size=batch_size,
        )

        updated_count += len(
            batch
        )

    return updated_count


# =========================================================
# Recalculate Fixed Products
# =========================================================


@transaction.atomic
def recalculate_fixed_products(
    *,
    batch_size=1000,
):

    pricing_settings = (
        PricingSettings.load()
    )

    queryset = (
        Product.objects
        .filter(
            pricing_mode=(
                Product
                .PricingMode
                .FIXED
            ),
            is_price_locked=False,
        )
        .exclude(
            status=(
                Product
                .Status
                .ARCHIVED
            )
        )
        .order_by(
            "pk"
        )
    )

    now = timezone.now()

    updated_count = 0

    batch = []

    for product in queryset.iterator(
        chunk_size=batch_size
    ):

        result = calculate_product_price(
            product=product,
            pricing_settings=(
                pricing_settings
            ),
        )

        product.current_price_toman = (
            result.final_price_toman
        )

        product.last_exchange_rate_toman = (
            None
        )

        product.price_updated_at = now

        batch.append(
            product
        )

        if len(batch) >= batch_size:

            Product.objects.bulk_update(
                batch,
                fields=[
                    "current_price_toman",
                    "last_exchange_rate_toman",
                    "price_updated_at",
                ],
                batch_size=batch_size,
            )

            updated_count += len(
                batch
            )

            batch.clear()

    if batch:

        Product.objects.bulk_update(
            batch,
            fields=[
                "current_price_toman",
                "last_exchange_rate_toman",
                "price_updated_at",
            ],
            batch_size=batch_size,
        )

        updated_count += len(
            batch
        )

    return updated_count


# =========================================================
# Activate Exchange Rate
# =========================================================


@transaction.atomic
def activate_exchange_rate(
    exchange_rate,
):

    # Rate انتخاب‌شده فعال می‌شود.
    #
    # ExchangeRate.save خودکار Rate فعال قبلی
    # همان Currency را غیرفعال می‌کند.
    exchange_rate.is_active = True

    exchange_rate.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    # فعلاً فقط USD روی محصولات اثر دارد.
    if exchange_rate.currency == "USD":

        updated_count = (
            recalculate_usd_products(
                exchange_rate=(
                    exchange_rate
                )
            )
        )

    else:

        updated_count = 0

    return updated_count