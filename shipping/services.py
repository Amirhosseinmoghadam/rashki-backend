from __future__ import annotations

from dataclasses import dataclass

from addresses.models import Address
from carts.models import Cart
from carts.services import (
    CartValidationError,
    calculate_cart,
)

from shipping.models import (
    ShippingMethod,
)

from shipping.origins.selectors import (
    ShippingOriginNotConfigured,
    get_default_shipping_origin,
)

from shipping.packaging.service import (
    CartPackagingError,
    build_cart_packages,
)

from shipping.providers.base import (
    ShippingProviderError,
)

from shipping.providers.registry import (
    get_shipping_provider,
)


# =========================================================
# Exceptions
# =========================================================


class ShippingError(Exception):
    pass


class ShippingValidationError(
    ShippingError
):
    pass


# =========================================================
# Quote result
# =========================================================


@dataclass
class ShippingQuote:
    method: ShippingMethod

    amount_toman: int | None

    weight_grams: int

    is_available: bool

    unavailable_reason: str | None = None

    provider_data: dict | None = None


# =========================================================
# Address
# =========================================================


def get_user_shipping_address(
    *,
    user,
    address_id,
):
    """
    فقط Address متعلق به خود User مجاز است.
    """

    try:
        address_id = int(
            address_id
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ShippingValidationError(
            "شناسه آدرس معتبر نیست."
        ) from exc

    address = (
        Address.objects
        .select_related(
            "province",
            "city",
        )
        .filter(
            pk=address_id,
            user=user,
        )
        .first()
    )

    if address is None:
        raise ShippingValidationError(
            "آدرس انتخاب‌شده پیدا نشد."
        )

    if not address.city_id:
        raise ShippingValidationError(
            (
                "شهر آدرس مقصد "
                "مشخص نشده است."
            )
        )

    return address


# =========================================================
# Cart
# =========================================================


def get_user_cart(
    *,
    user,
):
    """
    Cart فعلی User را برمی‌گرداند.

    برای Shipping Quote ساخت Cart جدید
    انجام نمی‌دهیم؛ Cart باید از قبل وجود داشته باشد.
    """

    cart = (
        Cart.objects
        .filter(
            user=user
        )
        .prefetch_related(
            "items__product"
        )
        .first()
    )

    if cart is None:
        raise ShippingValidationError(
            "سبد خرید وجود ندارد."
        )

    return cart


# =========================================================
# Cart pricing
# =========================================================


def calculate_shipping_cart(
    *,
    cart,
):
    """
    محاسبه strict سبد.

    اگر کالا:
        - ناموجود باشد
        - غیرقابل خرید باشد
        - قیمت نداشته باشد

    Checkout نباید ادامه پیدا کند.
    """

    try:
        calculation = calculate_cart(
            cart,
            strict=True,
        )

    except CartValidationError as exc:
        raise ShippingValidationError(
            str(exc)
        ) from exc

    if not calculation.get(
        "is_checkout_ready"
    ):
        raise ShippingValidationError(
            (
                "سبد خرید برای ثبت سفارش "
                "آماده نیست."
            )
        )

    return calculation


# =========================================================
# Declared package values
# =========================================================


def build_unit_values_by_cart_item_id(
    *,
    cart_calculation,
):
    """
    مقدار واقعی هر واحد کالا را از همان
    calculate_cart() دریافت می‌کند.

    فعلاً policy ما:

        declared value =
        current unit_price_toman

    بنابراین Shipping به Product model یا Pricing engine
    داخلی وابسته نیست؛ فقط خروجی رسمی Cart را می‌خواند.
    """

    result = {}

    items = (
        cart_calculation.get(
            "items"
        )
        or []
    )

    for item_data in items:

        if not item_data.get(
            "is_available"
        ):
            continue

        cart_item_id = (
            item_data.get(
                "id"
            )
        )

        unit_price_toman = (
            item_data.get(
                "unit_price_toman"
            )
        )

        if cart_item_id is None:
            raise ShippingValidationError(
                (
                    "شناسه یکی از آیتم‌های "
                    "سبد خرید مشخص نیست."
                )
            )

        if unit_price_toman is None:
            raise ShippingValidationError(
                (
                    "قیمت یکی از محصولات "
                    "سبد خرید مشخص نیست."
                )
            )

        try:
            unit_price_toman = int(
                unit_price_toman
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingValidationError(
                (
                    "قیمت یکی از محصولات "
                    "سبد خرید معتبر نیست."
                )
            ) from exc

        if unit_price_toman <= 0:
            raise ShippingValidationError(
                (
                    "قیمت یکی از محصولات "
                    "سبد خرید معتبر نیست."
                )
            )

        result[
            int(cart_item_id)
        ] = unit_price_toman

    if not result:
        raise ShippingValidationError(
            (
                "هیچ محصول قابل ارسال "
                "در سبد خرید وجود ندارد."
            )
        )

    return result


# =========================================================
# Build packages
# =========================================================


def build_shipping_packages(
    *,
    cart,
    cart_calculation,
):
    """
    Cart + Pricing
        ↓
    ShippingPackage[]

    هر Package شامل:
        weight
        dimensions
        selected Tipax box
        declared value
    """

    unit_values = (
        build_unit_values_by_cart_item_id(
            cart_calculation=(
                cart_calculation
            )
        )
    )

    try:
        packages = (
            build_cart_packages(
                cart=cart,
                unit_values_by_cart_item_id=(
                    unit_values
                ),
            )
        )

    except CartPackagingError as exc:
        raise ShippingValidationError(
            str(exc)
        ) from exc

    if not packages:
        raise ShippingValidationError(
            (
                "هیچ بسته‌ای برای "
                "ارسال ساخته نشد."
            )
        )

    return packages


# =========================================================
# Weight
# =========================================================


def calculate_packages_weight(
    packages,
):
    """
    وزن نهایی تمام Packageها.

    package_extra_weight_grams قبلاً داخل
    PackagingService روی هر Package اعمال شده است.
    """

    total = 0

    for package in packages:

        try:
            weight = int(
                package.weight_grams
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingValidationError(
                "وزن یکی از بسته‌ها معتبر نیست."
            ) from exc

        if weight <= 0:
            raise ShippingValidationError(
                "وزن یکی از بسته‌ها معتبر نیست."
            )

        total += weight

    if total <= 0:
        raise ShippingValidationError(
            "وزن کل مرسوله معتبر نیست."
        )

    return total


# =========================================================
# Total package declared value
# =========================================================


def calculate_packages_value(
    packages,
):
    """
    مجموع ارزش کالاهای داخل Packageها.

    باید با subtotal محصولات قابل ارسال برابر باشد
    چون declared value فعلاً از unit_price_toman می‌آید.
    """

    total = 0

    for package in packages:

        value = getattr(
            package,
            "declared_value_toman",
            None,
        )

        if value is None:
            raise ShippingValidationError(
                (
                    "ارزش یکی از بسته‌ها "
                    "مشخص نشده است."
                )
            )

        try:
            value = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingValidationError(
                (
                    "ارزش یکی از بسته‌ها "
                    "معتبر نیست."
                )
            ) from exc

        if value <= 0:
            raise ShippingValidationError(
                (
                    "ارزش یکی از بسته‌ها "
                    "معتبر نیست."
                )
            )

        total += value

    return total


# =========================================================
# Single method quote
# =========================================================


def quote_shipping_method(
    *,
    method,
    destination_address,
    weight_grams,
    package_value_toman=0,
    packages=None,
    origin=None,
):
    """
    یک ShippingMethod را Quote می‌کند.

    خطای یک Provider نباید باعث Crash شدن
    کل لیست روش‌های ارسال شود.
    """

    try:
        provider = (
            get_shipping_provider(
                method
            )
        )

        provider_quote = (
            provider.quote(
                method=method,

                destination_address=(
                    destination_address
                ),

                weight_grams=(
                    weight_grams
                ),

                package_value_toman=(
                    package_value_toman
                ),

                packages=packages,

                origin=origin,
            )
        )

        return ShippingQuote(
            method=method,

            amount_toman=int(
                provider_quote.amount_toman
            ),

            weight_grams=(
                weight_grams
            ),

            is_available=True,

            unavailable_reason=None,

            provider_data=(
                provider_quote.provider_data
                or {}
            ),
        )

    except ShippingProviderError as exc:

        return ShippingQuote(
            method=method,

            amount_toman=None,

            weight_grams=(
                weight_grams
            ),

            is_available=False,

            unavailable_reason=str(
                exc
            ),

            provider_data=None,
        )


# =========================================================
# All methods
# =========================================================


def get_shipping_quotes(
    *,
    user,
    address_id,
):
    """
    مسیر اصلی Shipping Quote.

    User
        ↓
    Address
        ↓
    Cart
        ↓
    calculate_cart(strict=True)
        ↓
    Product unit prices
        ↓
    PackagingService
        ↓
    ShippingPackage[]
        ↓
    Default ShippingOrigin
        ↓
    Providers
        ↓
    ShippingQuote[]
    """

    # -----------------------------------------------------
    # Destination
    # -----------------------------------------------------

    address = (
        get_user_shipping_address(
            user=user,
            address_id=address_id,
        )
    )

    # -----------------------------------------------------
    # Cart
    # -----------------------------------------------------

    cart = get_user_cart(
        user=user
    )

    cart_calculation = (
        calculate_shipping_cart(
            cart=cart
        )
    )

    # -----------------------------------------------------
    # Packages
    # -----------------------------------------------------

    packages = (
        build_shipping_packages(
            cart=cart,

            cart_calculation=(
                cart_calculation
            ),
        )
    )

    total_weight_grams = (
        calculate_packages_weight(
            packages
        )
    )

    package_value_toman = (
        calculate_packages_value(
            packages
        )
    )

    # -----------------------------------------------------
    # Origin snapshot for this Quote operation
    # -----------------------------------------------------

    try:
        origin = (
            get_default_shipping_origin()
        )

    except ShippingOriginNotConfigured as exc:
        raise ShippingValidationError(
            str(exc)
        ) from exc

    # -----------------------------------------------------
    # Active methods
    # -----------------------------------------------------

    methods = (
        ShippingMethod.objects
        .filter(
            is_active=True
        )
        .order_by(
            "sort_order",
            "id",
        )
    )

    quotes = []

    for method in methods:

        quote = (
            quote_shipping_method(
                method=method,

                destination_address=(
                    address
                ),

                weight_grams=(
                    total_weight_grams
                ),

                package_value_toman=(
                    package_value_toman
                ),

                packages=packages,

                origin=origin,
            )
        )

        quotes.append(
            quote
        )

    return (
        address,
        total_weight_grams,
        quotes,
    )


# =========================================================
# Selected method
# =========================================================


def get_selected_shipping_quote(
    *,
    user,
    address_id,
    shipping_method_id,
):
    """
    Checkout هرگز مبلغ Shipping ارسال‌شده از Client
    را قبول نمی‌کند.

    قیمت کاملاً Server-side دوباره محاسبه می‌شود.
    """

    try:
        shipping_method_id = int(
            shipping_method_id
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ShippingValidationError(
            (
                "روش ارسال انتخاب‌شده "
                "معتبر نیست."
            )
        ) from exc

    (
        address,
        total_weight_grams,
        quotes,
    ) = get_shipping_quotes(
        user=user,
        address_id=address_id,
    )

    selected_quote = None

    for quote in quotes:

        if (
            quote.method.id
            == shipping_method_id
        ):
            selected_quote = quote
            break

    if selected_quote is None:
        raise ShippingValidationError(
            (
                "روش ارسال انتخاب‌شده "
                "پیدا نشد."
            )
        )

    if not selected_quote.is_available:
        raise ShippingValidationError(
            (
                selected_quote
                .unavailable_reason
                or (
                    "روش ارسال انتخاب‌شده "
                    "در دسترس نیست."
                )
            )
        )

    return (
        address,
        total_weight_grams,
        selected_quote,
    )


def build_packages_from_cart_items(
    *,
    cart_items,
    unit_values_by_cart_item_id=None,
):
    """
    CartItemهای از قبل دریافت/Lock شده را
    بدون Query مجدد روی Cart به Package تبدیل می‌کند.

    این تابع مخصوص Checkout/Order creation مهم است،
    چون Productهای داخل cart_items همان Productهای
    select_for_update شده هستند.

    unit_values_by_cart_item_id:
        {
            cart_item_id: unit_price_toman,
        }
    """

    if unit_values_by_cart_item_id is None:
        unit_values_by_cart_item_id = {}

    cart_items = list(
        cart_items
    )

    if not cart_items:
        raise CartPackagingError(
            "سبد خرید خالی است."
        )

    packages = []

    for cart_item in cart_items:

        product = cart_item.product

        quantity = int(
            cart_item.quantity
        )

        if quantity <= 0:
            continue

        unit_value_toman = (
            unit_values_by_cart_item_id.get(
                cart_item.pk
            )
        )

        for _ in range(quantity):

            package = (
                build_single_product_package(
                    product=product,
                    declared_value_toman=(
                        unit_value_toman
                    ),
                )
            )

            packages.append(
                package
            )

    if not packages:
        raise CartPackagingError(
            "هیچ بسته‌ای برای سبد خرید ساخته نشد."
        )

    return packages