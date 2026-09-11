from __future__ import annotations

from decimal import Decimal

from shipping.models import (
    ShippingMethod,
    ShippingSettings,
)

from .base import (
    ShippingPackage,
    ShippingPackageItem,
)

from .selector import (
    PackagingSelectionError,
    select_tipax_carton_for_product,
)


class CartPackagingError(Exception):
    pass


# =========================================================
# Product validation
# =========================================================


def validate_product_shipping_data(
    product,
):
    """
    برای محاسبه بسته‌بندی فقط اطلاعات فیزیکی لازم است.

    قیمت عمداً اینجا بررسی نمی‌شود.
    """

    missing = []

    if not getattr(
        product,
        "weight_grams",
        None,
    ):
        missing.append(
            "weight_grams"
        )

    for field_name in (
        "shipping_length_cm",
        "shipping_width_cm",
        "shipping_height_cm",
    ):
        value = getattr(
            product,
            field_name,
            None,
        )

        if value is None:
            missing.append(
                field_name
            )

    if missing:
        raise CartPackagingError(
            (
                f"اطلاعات ارسال محصول «{product}» ناقص است: "
                + ", ".join(missing)
            )
        )


# =========================================================
# Single product → package
# =========================================================


def build_single_product_package(
    *,
    product,
    declared_value_toman=None,
):
    """
    یک واحد محصول را داخل کوچک‌ترین کارتن مناسب قرار می‌دهد.

    declared_value_toman اختیاری است چون:
        Packaging ≠ Pricing

    ارزش مرسوله بعداً از Cart/Checkout وارد می‌شود.
    """

    validate_product_shipping_data(
        product
    )

    try:
        selection = (
            select_tipax_carton_for_product(
                product=product,
                quantity=1,
            )
        )

    except PackagingSelectionError as exc:
        raise CartPackagingError(
            str(exc)
        ) from exc

    packing = selection.packing

    shipping_settings = (
        ShippingSettings.load()
    )

    extra_weight_grams = int(
        getattr(
            shipping_settings,
            "package_extra_weight_grams",
            0,
        )
        or 0
    )

    product_weight_grams = int(
        product.weight_grams
    )

    package_weight_grams = (
        product_weight_grams
        + extra_weight_grams
    )

    if declared_value_toman is not None:

        try:
            declared_value_toman = int(
                declared_value_toman
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise CartPackagingError(
                "ارزش مرسوله معتبر نیست."
            ) from exc

        if declared_value_toman <= 0:
            raise CartPackagingError(
                "ارزش مرسوله باید بیشتر از صفر باشد."
            )

    item = ShippingPackageItem(
        product_id=product.pk,

        product_name=str(
            product
        ),

        quantity=1,

        weight_grams=(
            product_weight_grams
        ),

        length_cm=Decimal(
            str(
                product.shipping_length_cm
            )
        ),

        width_cm=Decimal(
            str(
                product.shipping_width_cm
            )
        ),

        height_cm=Decimal(
            str(
                product.shipping_height_cm
            )
        ),
    )

    return ShippingPackage(
        weight_grams=(
            package_weight_grams
        ),

        # ابعاد نهایی بسته برای شرکت حمل
        length_cm=Decimal(
            str(
                packing.length
            )
        ),

        width_cm=Decimal(
            str(
                packing.width
            )
        ),

        height_cm=Decimal(
            str(
                packing.height
            )
        ),

        items=(
            item,
        ),

        declared_value_toman=(
            declared_value_toman
        ),

        provider_packing_id=int(
            packing.provider_packing_id
        ),

        provider_packing_title=(
            packing.title
        ),

        box_number=(
            packing.box_number
        ),

        pack_type=(
            packing.pack_type
        ),

        # Reference واقعی Tipax:
        # یدکی و لوازم خودرو موتور
        package_content_id=12,

        # ParcelType:
        # بسته
        parcel_type_id=5,

        metadata={
            "provider": (
                ShippingMethod
                .Provider
                .TIPAX
            ),

            "packing_option_pk": (
                packing.pk
            ),

            "product_dimensions": {
                "length": str(
                    product.shipping_length_cm
                ),

                "width": str(
                    product.shipping_width_cm
                ),

                "height": str(
                    product.shipping_height_cm
                ),
            },
        },
    )


# =========================================================
# Cart → Packages
# =========================================================

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



def build_cart_packages(
    *,
    cart,
    unit_values_by_cart_item_id=None,
):
    """
    نسخه عمومی برای Cart عادی.

    برای Checkout قفل‌شده از:
        build_packages_from_cart_items()

    استفاده می‌کنیم.
    """

    cart_items = list(
        cart.items
        .select_related(
            "product"
        )
        .all()
    )

    return build_packages_from_cart_items(
        cart_items=cart_items,
        unit_values_by_cart_item_id=(
            unit_values_by_cart_item_id
        ),
    )