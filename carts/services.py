from django.db import transaction

from products.models import Product

from discounts.services import (
    DiscountLine,
    DiscountValidationError,
    calculate_discount,
    get_discount_by_code,
)

from .constants import (
    MAX_CART_DISTINCT_ITEMS,
    MAX_CART_ITEM_QUANTITY,
)

from .models import (
    Cart,
    CartItem,
)

from .selectors import (
    get_cart_queryset,
    get_public_category_ids,
    get_purchasable_products_queryset,
)


# =========================================================
# Exceptions
# =========================================================


class CartError(Exception):
    pass


class CartValidationError(
    CartError
):
    pass


class CartItemNotFoundError(
    CartError
):
    pass


# =========================================================
# Get / Create Cart
# =========================================================


def get_or_create_cart(
    user,
):

    cart, _ = (
        Cart.objects.get_or_create(
            user=user
        )
    )

    return cart


# =========================================================
# Reload Cart
# =========================================================


def get_cart(
    user,
):

    cart = get_or_create_cart(
        user
    )

    return (
        get_cart_queryset()
        .get(
            pk=cart.pk
        )
    )


# =========================================================
# Product Availability
# =========================================================


def get_item_availability(
    product,
    quantity,
    public_category_ids,
):
    """
    وضعیت فعلی Product را برای Cart بررسی می‌کند.
    """

    # Product دیگر Public نیست.
    if (
        product.status
        != Product.Status.ACTIVE
    ):

        return (
            False,
            "این محصول در حال حاضر قابل خرید نیست.",
        )

    # Category یا یکی از Parentها غیرفعال است.
    if (
        product.category_id
        not in public_category_ids
    ):

        return (
            False,
            "دسته‌بندی این محصول در حال حاضر فعال نیست.",
        )

    # Brand غیرفعال است.
    if (
        product.brand_id
        and not product.brand.is_active
    ):

        return (
            False,
            "برند این محصول در حال حاضر فعال نیست.",
        )

    # Product قیمت ندارد.
    if (
        product.current_price_toman
        is None
    ):

        return (
            False,
            "قیمت این محصول در حال حاضر مشخص نیست.",
        )

    # موجودی صفر.
    if product.stock_quantity <= 0:

        return (
            False,
            "این محصول در حال حاضر ناموجود است.",
        )

    # Quantity بیشتر از Stock فعلی است.
    if quantity > product.stock_quantity:

        return (
            False,
            (
                "تعداد درخواستی بیشتر از "
                f"موجودی فعلی ({product.stock_quantity}) است."
            ),
        )

    return (
        True,
        None,
    )


# =========================================================
# Calculate Cart
# =========================================================


def calculate_cart(
    cart,
    *,
    strict=False,
):
    """
    Cart را بر اساس قیمت و موجودی فعلی
    Productها محاسبه می‌کند.

    strict=True:
        برای Checkout استفاده خواهد شد.
        وجود هر Product نامعتبر باعث Error می‌شود.
    """

    public_category_ids = set(
        get_public_category_ids()
    )

    item_results = []

    discount_lines = []

    subtotal_toman = 0

    total_quantity = 0

    has_issues = False

    # =====================================================
    # Items
    # =====================================================

    for item in cart.items.all():

        product = item.product

        (
            is_available,
            availability_message,
        ) = get_item_availability(
            product,
            item.quantity,
            public_category_ids,
        )

        unit_price = (
            product.current_price_toman
        )

        line_total = (
            unit_price * item.quantity
            if unit_price is not None
            else None
        )

        if not is_available:

            has_issues = True

        else:

            subtotal_toman += (
                line_total
            )

            discount_lines.append(
                DiscountLine(
                    product=product,
                    quantity=item.quantity,
                    unit_price_toman=(
                        unit_price
                    ),
                )
            )

        total_quantity += (
            item.quantity
        )

        item_results.append(
            {
                "id": item.id,
                "product": product,
                "quantity": item.quantity,
                "unit_price_toman": (
                    unit_price
                ),
                "line_total_toman": (
                    line_total
                ),
                "is_available": (
                    is_available
                ),
                "availability_message": (
                    availability_message
                ),
                "available_stock": (
                    product.stock_quantity
                ),
                "created_at": (
                    item.created_at
                ),
                "updated_at": (
                    item.updated_at
                ),
            }
        )

    # =====================================================
    # Strict
    # =====================================================

    if strict:

        if not item_results:

            raise CartValidationError(
                "سبد خرید خالی است."
            )

        if has_issues:

            raise CartValidationError(
                "سبد خرید دارای محصول نامعتبر "
                "یا ناموجود است. ابتدا سبد را اصلاح کنید."
            )

    # =====================================================
    # Discount
    # =====================================================

    discount_data = None

    discount_valid = None

    discount_error = None

    discount_amount_toman = 0

    final_subtotal_toman = (
        subtotal_toman
    )

    if cart.applied_discount_id:

        discount_data = {
            "id": cart.applied_discount.id,
            "code": cart.applied_discount.code,
            "discount_type": (
                cart.applied_discount
                .discount_type
            ),
            "scope": (
                cart.applied_discount.scope
            ),
        }

        if has_issues:

            discount_valid = False

            discount_error = (
                "برای محاسبه کد تخفیف "
                "ابتدا مشکلات سبد خرید را برطرف کنید."
            )

        else:

            try:

                discount_result = (
                    calculate_discount(
                        discount=(
                            cart
                            .applied_discount
                        ),
                        lines=discount_lines,
                        user=cart.user,
                    )
                )

                discount_valid = True

                discount_amount_toman = (
                    discount_result
                    .discount_amount_toman
                )

                final_subtotal_toman = (
                    discount_result
                    .final_subtotal_toman
                )

                discount_data.update(
                    {
                        "eligible_subtotal_toman": (
                            discount_result
                            .eligible_subtotal_toman
                        ),
                        "discount_amount_toman": (
                            discount_amount_toman
                        ),
                    }
                )

            except (
                DiscountValidationError
            ) as exc:

                discount_valid = False

                discount_error = str(
                    exc
                )

    # =====================================================
    # Result
    # =====================================================

    return {
        "id": cart.id,

        "items": item_results,

        # تعداد Productهای متفاوت.
        "item_count": len(
            item_results
        ),

        # مجموع Quantity تمام Productها.
        "total_quantity": (
            total_quantity
        ),

        # مبلغ محصولات معتبر قبل از تخفیف.
        "subtotal_toman": (
            subtotal_toman
        ),

        "applied_discount": (
            discount_data
        ),

        "discount_valid": (
            discount_valid
        ),

        "discount_error": (
            discount_error
        ),

        "discount_amount_toman": (
            discount_amount_toman
        ),

        # هزینه ارسال هنوز اضافه نشده است.
        "final_subtotal_toman": (
            final_subtotal_toman
        ),

        "has_issues": (
            has_issues
        ),

        "is_checkout_ready": (
            bool(item_results)
            and not has_issues
        ),

        "created_at": (
            cart.created_at
        ),

        "updated_at": (
            cart.updated_at
        ),
    }


# =========================================================
# Add Item
# =========================================================


@transaction.atomic
def add_cart_item(
    *,
    user,
    product_id,
    quantity=1,
):

    if quantity < 1:

        raise CartValidationError(
            "تعداد باید حداقل 1 باشد."
        )

    if (
        quantity
        > MAX_CART_ITEM_QUANTITY
    ):

        raise CartValidationError(
            (
                "حداکثر تعداد مجاز برای "
                f"هر محصول {MAX_CART_ITEM_QUANTITY} است."
            )
        )

    cart = get_or_create_cart(
        user
    )

    # Cart برای جلوگیری از چند تغییر
    # همزمان Lock می‌شود.
    cart = (
        Cart.objects
        .select_for_update()
        .get(
            pk=cart.pk
        )
    )

    product = (
        get_purchasable_products_queryset()
        .filter(
            pk=product_id
        )
        .first()
    )

    if product is None:

        raise CartValidationError(
            "محصول موردنظر در حال حاضر "
            "قابل خرید نیست."
        )

    if product.stock_quantity <= 0:

        raise CartValidationError(
            "محصول موردنظر ناموجود است."
        )

    item = (
        CartItem.objects
        .select_for_update()
        .filter(
            cart=cart,
            product=product,
        )
        .first()
    )

    # =====================================================
    # Existing Item
    # =====================================================

    if item:

        new_quantity = (
            item.quantity
            + quantity
        )

        if (
            new_quantity
            > MAX_CART_ITEM_QUANTITY
        ):

            raise CartValidationError(
                (
                    "حداکثر تعداد مجاز برای "
                    f"این محصول "
                    f"{MAX_CART_ITEM_QUANTITY} است."
                )
            )

        if (
            new_quantity
            > product.stock_quantity
        ):

            raise CartValidationError(
                (
                    "موجودی کافی نیست. "
                    f"موجودی فعلی "
                    f"{product.stock_quantity} عدد است."
                )
            )

        item.quantity = (
            new_quantity
        )

        item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        created = False

    # =====================================================
    # New Item
    # =====================================================

    else:

        distinct_count = (
            CartItem.objects
            .filter(
                cart=cart
            )
            .count()
        )

        if (
            distinct_count
            >= MAX_CART_DISTINCT_ITEMS
        ):

            raise CartValidationError(
                (
                    "حداکثر تعداد محصولات "
                    "متفاوت در سبد خرید "
                    f"{MAX_CART_DISTINCT_ITEMS} است."
                )
            )

        if (
            quantity
            > product.stock_quantity
        ):

            raise CartValidationError(
                (
                    "موجودی کافی نیست. "
                    f"موجودی فعلی "
                    f"{product.stock_quantity} عدد است."
                )
            )

        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
        )

        created = True

    return (
        get_cart(user),
        created,
    )


# =========================================================
# Update Item Quantity
# =========================================================


@transaction.atomic
def update_cart_item(
    *,
    user,
    product_id,
    quantity,
):

    if quantity < 1:

        raise CartValidationError(
            "تعداد باید حداقل 1 باشد."
        )

    if (
        quantity
        > MAX_CART_ITEM_QUANTITY
    ):

        raise CartValidationError(
            (
                "حداکثر تعداد مجاز برای "
                f"هر محصول {MAX_CART_ITEM_QUANTITY} است."
            )
        )

    cart = get_or_create_cart(
        user
    )

    cart = (
        Cart.objects
        .select_for_update()
        .get(
            pk=cart.pk
        )
    )

    item = (
        CartItem.objects
        .select_for_update()
        .select_related(
            "product",
            "product__category",
            "product__brand",
        )
        .filter(
            cart=cart,
            product_id=product_id,
        )
        .first()
    )

    if item is None:

        raise CartItemNotFoundError(
            "این محصول در سبد خرید "
            "وجود ندارد."
        )

    product = item.product

    public_category_ids = set(
        get_public_category_ids()
    )

    (
        is_available,
        message,
    ) = get_item_availability(
        product,
        quantity,
        public_category_ids,
    )

    if not is_available:

        raise CartValidationError(
            message
        )

    item.quantity = quantity

    item.save(
        update_fields=[
            "quantity",
            "updated_at",
        ]
    )

    return get_cart(
        user
    )


# =========================================================
# Remove Item
# =========================================================


@transaction.atomic
def remove_cart_item(
    *,
    user,
    product_id,
):

    cart = get_or_create_cart(
        user
    )

    item = (
        CartItem.objects
        .filter(
            cart=cart,
            product_id=product_id,
        )
        .first()
    )

    if item is None:

        raise CartItemNotFoundError(
            "این محصول در سبد خرید "
            "وجود ندارد."
        )

    item.delete()

    return get_cart(
        user
    )


# =========================================================
# Clear Cart
# =========================================================


@transaction.atomic
def clear_cart(
    user,
):

    cart = get_or_create_cart(
        user
    )

    CartItem.objects.filter(
        cart=cart
    ).delete()

    # Discount نیز هنگام Clear Cart حذف می‌شود.
    if cart.applied_discount_id:

        cart.applied_discount = None

        cart.save(
            update_fields=[
                "applied_discount",
                "updated_at",
            ]
        )

    return get_cart(
        user
    )


# =========================================================
# Apply Discount
# =========================================================


@transaction.atomic
def apply_cart_discount(
    *,
    user,
    code,
):

    cart = get_cart(
        user
    )

    # قبل از اعمال Discount، Cart باید
    # از نظر Product/Stock سالم باشد.
    calculation = calculate_cart(
        cart,
        strict=True,
    )

    discount = get_discount_by_code(
        code
    )

    lines = []

    for item_data in calculation[
        "items"
    ]:

        lines.append(
            DiscountLine(
                product=(
                    item_data[
                        "product"
                    ]
                ),
                quantity=(
                    item_data[
                        "quantity"
                    ]
                ),
                unit_price_toman=(
                    item_data[
                        "unit_price_toman"
                    ]
                ),
            )
        )

    # فقط Validation.
    # Usage در Cart ثبت نمی‌شود.
    calculate_discount(
        discount=discount,
        lines=lines,
        user=user,
    )

    locked_cart = (
        Cart.objects
        .select_for_update()
        .get(
            pk=cart.pk
        )
    )

    locked_cart.applied_discount = (
        discount
    )

    locked_cart.save(
        update_fields=[
            "applied_discount",
            "updated_at",
        ]
    )

    return get_cart(
        user
    )


# =========================================================
# Remove Discount
# =========================================================


@transaction.atomic
def remove_cart_discount(
    user,
):

    cart = get_or_create_cart(
        user
    )

    cart = (
        Cart.objects
        .select_for_update()
        .get(
            pk=cart.pk
        )
    )

    cart.applied_discount = None

    cart.save(
        update_fields=[
            "applied_discount",
            "updated_at",
        ]
    )

    return get_cart(
        user
    )