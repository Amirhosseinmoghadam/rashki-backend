import uuid

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from addresses.models import Address

from carts.models import (
    Cart,
    CartItem,
)

from carts.selectors import (
    get_public_category_ids,
)

from discounts.services import (
    DiscountLine,
    DiscountValidationError,
    calculate_discount,
    consume_discount,
    revoke_discount_usage,
)

from products.models import Product

from shipping.models import (
    ShippingSettings,
    ShippingMethod,
    ShippingProviderOriginMap,
    TipaxSettings,
)

from .models import (
    Order,
    OrderItem,
)

from .selectors import (
    get_order_queryset,
)

from shipping.origins.selectors import (
    ShippingOriginNotConfigured,
    get_default_shipping_origin,
)

from shipping.packaging.service import (
    CartPackagingError,
    build_packages_from_cart_items,
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


class OrderError(Exception):
    pass


class OrderValidationError(
    OrderError
):
    pass


class OrderNotFoundError(
    OrderError
):
    pass


class InvalidOrderTransitionError(
    OrderError
):
    pass


# =========================================================
# Order Number
# =========================================================


def generate_order_number():

    while True:

        date_part = (
            timezone.now()
            .strftime("%Y%m%d")
        )

        random_part = (
            uuid.uuid4()
            .hex[:8]
            .upper()
        )

        order_number = (
            f"RK-{date_part}-"
            f"{random_part}"
        )

        if not Order.objects.filter(
            order_number=order_number
        ).exists():

            return order_number


# =========================================================
# Address
# =========================================================


def get_checkout_address(
    *,
    user,
    address_id,
):

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

        raise OrderValidationError(
            "آدرس انتخاب‌شده معتبر نیست."
        )

    return address


# =========================================================
# Shipping Weight
# =========================================================


def calculate_locked_package_weight(
    locked_items,
):

    total = 0

    for item in locked_items:

        product = item.product

        if product.weight_grams is None:

            raise OrderValidationError(
                (
                    f"وزن محصول «{product.name}» "
                    "تعریف نشده است."
                )
            )

        total += (
            product.weight_grams
            * item.quantity
        )

    shipping_settings = (
        ShippingSettings.load()
    )

    total += (
        shipping_settings
        .package_extra_weight_grams
    )

    if total <= 0:

        raise OrderValidationError(
            "وزن مرسوله نامعتبر است."
        )

    return total


# =========================================================
# Validate Product
# =========================================================


def validate_locked_product(
    *,
    product,
    quantity,
    public_category_ids,
):

    if (
        product.status
        != Product.Status.ACTIVE
    ):

        raise OrderValidationError(
            (
                f"محصول «{product.name}» "
                "در حال حاضر قابل خرید نیست."
            )
        )

    if (
        product.category_id
        not in public_category_ids
    ):

        raise OrderValidationError(
            (
                f"دسته‌بندی محصول "
                f"«{product.name}» فعال نیست."
            )
        )

    if (
        product.brand_id
        and not product.brand.is_active
    ):

        raise OrderValidationError(
            (
                f"برند محصول "
                f"«{product.name}» فعال نیست."
            )
        )

    if (
        product.current_price_toman
        is None
    ):

        raise OrderValidationError(
            (
                f"قیمت محصول "
                f"«{product.name}» مشخص نیست."
            )
        )

    if quantity > product.stock_quantity:

        raise OrderValidationError(
            (
                f"موجودی «{product.name}» "
                f"کافی نیست. موجودی فعلی "
                f"{product.stock_quantity} عدد است."
            )
        )


# =========================================================
# Create Order
# =========================================================


@transaction.atomic
def create_order_from_cart(
    *,
    user,
    address_id,
    shipping_method_id,
    accept_terms,
    customer_note="",
):
    """
    ساخت Order نهایی از Cart.

    ویژگی‌های مهم:

    - Cart و Productها Lock می‌شوند.
    - قیمت و موجودی دوباره اعتبارسنجی می‌شوند.
    - Packageها از ابعاد/وزن Productهای Lock شده ساخته می‌شوند.
    - باکس مناسب Tipax انتخاب می‌شود.
    - مبدا فعلی Shipping فقط برای همین Order گرفته می‌شود.
    - Quote دوباره Server-side محاسبه می‌شود.
    - Origin / Package / Service / Rate داخل Order Snapshot می‌شوند.
    - تغییرات بعدی Product، باکس یا مبدا روی Order قبلی اثر ندارد.
    """

    # =====================================================
    # Terms
    # =====================================================

    if accept_terms is not True:

        raise OrderValidationError(
            "پذیرش قوانین و شرایط "
            "برای ثبت سفارش الزامی است."
        )

    now = timezone.now()

    # =====================================================
    # Lock Cart
    # =====================================================

    cart = (
        Cart.objects
        .select_for_update()
        .select_related(
            "applied_discount",
        )
        .filter(
            user=user
        )
        .first()
    )

    if cart is None:

        raise OrderValidationError(
            "سبد خرید خالی است."
        )

    # =====================================================
    # Lock Cart Items
    # =====================================================

    cart_items = list(
        CartItem.objects
        .select_for_update()
        .filter(
            cart=cart
        )
        .order_by(
            "id"
        )
    )

    if not cart_items:

        raise OrderValidationError(
            "سبد خرید خالی است."
        )

    # =====================================================
    # Lock Products
    # =====================================================

    product_ids = [
        item.product_id
        for item in cart_items
    ]

    locked_products = {
        product.id: product
        for product in (
            Product.objects
            .select_for_update()
            .select_related(
                "category",
                "brand",
            )
            .filter(
                id__in=product_ids
            )
            .order_by(
                "id"
            )
        )
    }

    if (
        len(locked_products)
        != len(set(product_ids))
    ):

        raise OrderValidationError(
            "یک یا چند محصول سبد "
            "دیگر وجود ندارند."
        )

    # CartItemها باید دقیقاً از Productهای Lock شده استفاده کنند.
    for item in cart_items:

        item.product = (
            locked_products[
                item.product_id
            ]
        )

    # =====================================================
    # Product Validation + Prices
    # =====================================================

    public_category_ids = set(
        get_public_category_ids()
    )

    subtotal_toman = 0

    discount_lines = []

    unit_values_by_cart_item_id = {}

    for item in cart_items:

        product = item.product

        validate_locked_product(
            product=product,
            quantity=item.quantity,
            public_category_ids=(
                public_category_ids
            ),
        )

        unit_price_toman = int(
            product.current_price_toman
        )

        line_total_toman = (
            unit_price_toman
            * item.quantity
        )

        subtotal_toman += (
            line_total_toman
        )

        # برای declared value هر Package.
        unit_values_by_cart_item_id[
            item.pk
        ] = unit_price_toman

        discount_lines.append(
            DiscountLine(
                product=product,
                quantity=item.quantity,
                unit_price_toman=(
                    unit_price_toman
                ),
            )
        )

    # =====================================================
    # Destination Address
    # =====================================================

    address = get_checkout_address(
        user=user,
        address_id=address_id,
    )

    # =====================================================
    # Discount
    # =====================================================

    discount = (
        cart.applied_discount
    )

    discount_amount_toman = 0
    eligible_discount_subtotal = 0

    if discount is not None:

        try:

            discount_result = (
                calculate_discount(
                    discount=discount,
                    lines=discount_lines,
                    user=user,
                )
            )

        except DiscountValidationError as exc:

            raise OrderValidationError(
                str(exc)
            ) from exc

        discount_amount_toman = (
            discount_result
            .discount_amount_toman
        )

        eligible_discount_subtotal = (
            discount_result
            .eligible_subtotal_toman
        )

    # =====================================================
    # Shipping Method
    # =====================================================

    shipping_method = (
        ShippingMethod.objects
        .filter(
            pk=shipping_method_id,
            is_active=True,
        )
        .first()
    )

    if shipping_method is None:

        raise OrderValidationError(
            "روش ارسال معتبر نیست."
        )

    # =====================================================
    # Build Shipping Packages
    # =====================================================

    try:

        packages = (
            build_packages_from_cart_items(
                cart_items=cart_items,
                unit_values_by_cart_item_id=(
                    unit_values_by_cart_item_id
                ),
            )
        )

    except CartPackagingError as exc:

        raise OrderValidationError(
            str(exc)
        ) from exc

    # =====================================================
    # Shipping Weight
    # =====================================================

    shipping_weight = sum(
        int(
            package.weight_grams
        )
        for package in packages
    )

    if shipping_weight <= 0:

        raise OrderValidationError(
            "وزن نهایی مرسوله نامعتبر است."
        )

    # =====================================================
    # Package Declared Value
    # =====================================================

    package_value_toman = 0

    for package in packages:

        if (
            package.declared_value_toman
            is None
        ):

            raise OrderValidationError(
                (
                    "ارزش یکی از بسته‌های "
                    "ارسال مشخص نشده است."
                )
            )

        package_value_toman += int(
            package.declared_value_toman
        )

    if package_value_toman <= 0:

        raise OrderValidationError(
            "ارزش مرسوله نامعتبر است."
        )

    # =====================================================
    # Current Default Origin
    # =====================================================

    try:

        shipping_origin = (
            get_default_shipping_origin()
        )

        # =====================================================
        # Provider Origin Map
        # =====================================================

        provider_origin_map = (
            ShippingProviderOriginMap.objects
            .filter(
                provider=shipping_method.provider,
                origin=shipping_origin,
                is_active=True,
            )
            .first()
        )

        if (
                shipping_method.provider == "tipax"
                and provider_origin_map is None
        ):
            raise OrderValidationError(
                (
                    "مبدا ارسال در Tipax "
                    "ثبت یا Map نشده است."
                )
            )

    except ShippingOriginNotConfigured as exc:

        raise OrderValidationError(
            str(exc)
        ) from exc

    # =====================================================
    # Shipping Quote
    # =====================================================

    provider = get_shipping_provider(
        shipping_method
    )

    try:

        shipping_quote = (
            provider.quote(
                method=shipping_method,

                destination_address=(
                    address
                ),

                weight_grams=(
                    shipping_weight
                ),

                package_value_toman=(
                    package_value_toman
                ),

                packages=(
                    packages
                ),

                origin=(
                    shipping_origin
                ),
            )
        )

    except ShippingProviderError as exc:

        raise OrderValidationError(
            str(exc)
        ) from exc

    try:

        shipping_amount = int(
            shipping_quote.amount_toman
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise OrderValidationError(
            "هزینه ارسال معتبر نیست."
        ) from exc

    if shipping_amount < 0:

        raise OrderValidationError(
            "هزینه ارسال معتبر نیست."
        )

    # =====================================================
    # Shipping Snapshot
    # =====================================================

    shipping_provider_data = dict(
        shipping_quote.provider_data
        or {}
    )
    # =====================================================
    # Tipax Shipment Options Snapshot
    # =====================================================

    if shipping_method.provider == "tipax":

        tipax_settings = (
            TipaxSettings.objects.first()
        )

        if tipax_settings is None:
            raise OrderValidationError(
                "تنظیمات Tipax تعریف نشده است."
            )

        shipping_provider_data[
            "shipment_options"
        ] = {
            "payment_type": (
                tipax_settings.payment_type
            ),
            "pickup_type": (
                tipax_settings.pickup_type
            ),
            "distribution_type": (
                tipax_settings.distribution_type
            ),
            "enable_label_privacy": (
                tipax_settings
                .enable_label_privacy
            ),
            "customer_substation_code": (
                    tipax_settings
                    .customer_substation_code
                    or ""
            ),
        }

    # =====================================================
    # Freeze Provider Origin Address
    # =====================================================

    origin_snapshot = dict(
        shipping_provider_data.get(
            "origin"
        )
        or {}
    )

    if provider_origin_map:
        origin_snapshot.update(
            {
                "provider_address_id": (
                    provider_origin_map
                    .provider_address_id
                ),

                "provider_address_title": (
                    provider_origin_map
                    .provider_address_title
                ),
            }
        )

    shipping_provider_data[
        "origin"
    ] = origin_snapshot


    # اطلاعات عمومی Quote را هم Snapshot می‌کنیم،
    # حتی اگر Provider در آینده ساختارش تغییر کند.
    shipping_provider_data.update(
        {
            "snapshot_version": 1,

            "quoted_at": (
                now.isoformat()
            ),

            "method_snapshot": {
                "id": (
                    shipping_method.id
                ),

                "code": (
                    shipping_method.code
                ),

                "name": (
                    shipping_method.name
                ),

                "provider": (
                    shipping_method.provider
                ),

                "service_code": (
                    shipping_method
                    .service_code
                ),
            },

            "shipping_amount_toman": (
                shipping_amount
            ),

            "shipping_weight_grams": (
                shipping_weight
            ),

            "package_value_toman": (
                package_value_toman
            ),
        }
    )

    # =====================================================
    # Total
    # =====================================================

    total_toman = (
        subtotal_toman
        - discount_amount_toman
        + shipping_amount
    )

    if total_toman < 0:

        raise OrderValidationError(
            "مبلغ نهایی سفارش نامعتبر است."
        )

    # =====================================================
    # Expiry
    # =====================================================

    timeout_minutes = getattr(
        settings,
        "ORDER_PAYMENT_TIMEOUT_MINUTES",
        20,
    )

    expires_at = (
        now
        +
        timedelta(
            minutes=(
                timeout_minutes
            )
        )
    )

    # =====================================================
    # Create Order
    # =====================================================

    order = Order.objects.create(

        order_number=(
            generate_order_number()
        ),

        user=user,

        status=(
            Order.Status
            .PENDING_PAYMENT
        ),

        payment_status=(
            Order.PaymentStatus
            .UNPAID
        ),

        # -----------------------------------------
        # Destination Address Snapshot
        # -----------------------------------------

        address=address,

        shipping_first_name=(
            address.first_name
        ),

        shipping_last_name=(
            address.last_name
        ),

        shipping_mobile_number=(
            address.mobile_number
        ),

        shipping_phone_number=(
            address.phone_number
            or ""
        ),

        shipping_province_name=(
            address.province.name
        ),

        shipping_city_name=(
            address.city.name
        ),

        shipping_postal_code=(
            address.postal_code
        ),

        shipping_postal_address=(
            address.postal_address
        ),

        # -----------------------------------------
        # Shipping Snapshot
        # -----------------------------------------

        shipping_method=(
            shipping_method
        ),

        shipping_method_code=(
            shipping_method.code
        ),

        shipping_method_name=(
            shipping_method.name
        ),

        shipping_provider=(
            shipping_method.provider
        ),

        shipping_service_code=(
            shipping_method
            .service_code
        ),

        shipping_weight_grams=(
            shipping_weight
        ),

        shipping_provider_data=(
            shipping_provider_data
        ),

        # -----------------------------------------
        # Discount Snapshot
        # -----------------------------------------

        discount=discount,

        discount_code=(
            discount.code
            if discount
            else ""
        ),

        discount_type=(
            discount.discount_type
            if discount
            else ""
        ),

        discount_scope=(
            discount.scope
            if discount
            else ""
        ),

        # -----------------------------------------
        # Money
        # -----------------------------------------

        subtotal_toman=(
            subtotal_toman
        ),

        eligible_discount_subtotal_toman=(
            eligible_discount_subtotal
        ),

        discount_amount_toman=(
            discount_amount_toman
        ),

        shipping_amount_toman=(
            shipping_amount
        ),

        total_toman=(
            total_toman
        ),

        # -----------------------------------------
        # Customer
        # -----------------------------------------

        customer_note=(
            customer_note.strip()
        ),

        terms_accepted_at=now,

        # -----------------------------------------
        # Stock
        # -----------------------------------------

        stock_reserved_at=now,

        # -----------------------------------------
        # Payment
        # -----------------------------------------

        expires_at=(
            expires_at
        ),
    )

    # =====================================================
    # Order Item Snapshots
    # =====================================================

    order_items = []

    for cart_item in cart_items:

        product = (
            cart_item.product
        )

        unit_price = int(
            product.current_price_toman
        )

        order_items.append(
            OrderItem(
                order=order,

                product=product,

                product_id_snapshot=(
                    product.id
                ),

                product_name=(
                    product.name
                ),

                product_slug=(
                    product.slug
                ),

                product_sku=(
                    product.sku
                    or ""
                ),

                product_brand_name=(
                    product.brand.name
                    if product.brand
                    else ""
                ),

                product_unit=(
                    product.unit
                ),

                unit_price_toman=(
                    unit_price
                ),

                quantity=(
                    cart_item.quantity
                ),

                total_price_toman=(
                    unit_price
                    * cart_item.quantity
                ),
            )
        )

    OrderItem.objects.bulk_create(
        order_items
    )

    # =====================================================
    # Reserve Stock
    # =====================================================

    products_to_update = []

    for item in cart_items:

        product = (
            item.product
        )

        product.stock_quantity -= (
            item.quantity
        )

        products_to_update.append(
            product
        )

    Product.objects.bulk_update(
        products_to_update,
        fields=[
            "stock_quantity",
        ],
    )

    # =====================================================
    # Consume Discount
    # =====================================================

    if discount is not None:

        try:

            consume_discount(
                discount=discount,
                user=user,
                lines=discount_lines,
                reference=(
                    order.order_number
                ),
            )

        except DiscountValidationError as exc:

            # کل Transaction Rollback می‌شود:
            # Order
            # OrderItems
            # Stock
            # Discount usage
            raise OrderValidationError(
                str(exc)
            ) from exc

    # =====================================================
    # Clear Cart
    # =====================================================

    CartItem.objects.filter(
        cart=cart
    ).delete()

    cart.applied_discount = None

    cart.save(
        update_fields=[
            "applied_discount",
            "updated_at",
        ]
    )

    # =====================================================
    # Return fresh Order
    # =====================================================

    return (
        get_order_queryset()
        .get(
            pk=order.pk
        )
    )
# =========================================================
# Release Stock
# =========================================================


def _release_order_stock(
    order,
):

    if order.stock_released_at is not None:
        return

    items = list(
        OrderItem.objects
        .filter(
            order=order
        )
        .order_by(
            "product_id"
        )
    )

    product_ids = [
        item.product_id
        for item in items
    ]

    products = {
        product.id: product
        for product
        in Product.objects
        .select_for_update()
        .filter(
            id__in=product_ids
        )
        .order_by(
            "id"
        )
    }

    for item in items:

        product = products[
            item.product_id
        ]

        product.stock_quantity += (
            item.quantity
        )

    Product.objects.bulk_update(
        list(products.values()),
        fields=[
            "stock_quantity",
        ],
    )

    order.stock_released_at = (
        timezone.now()
    )


# =========================================================
# Cancel Unpaid Order
# =========================================================


@transaction.atomic
def cancel_unpaid_order(
    *,
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    if (
        order.status
        != Order.Status.PENDING_PAYMENT
    ):

        raise InvalidOrderTransitionError(
            "این سفارش در وضعیت قابل "
            "لغو توسط کاربر نیست."
        )

    if (
        order.payment_status
        not in {
            Order.PaymentStatus.UNPAID,
            Order.PaymentStatus.FAILED,
        }
    ):

        raise InvalidOrderTransitionError(
            "وضعیت پرداخت این سفارش "
            "اجازه لغو مستقیم را نمی‌دهد."
        )

    _release_order_stock(
        order
    )

    if order.discount_id:

        try:

            revoke_discount_usage(
                order.order_number
            )

        except DiscountValidationError:

            # اگر Usage وجود نداشت،
            # لغو Order نباید Fail شود.
            pass

    now = timezone.now()

    order.status = (
        Order.Status.CANCELLED
    )

    order.cancelled_at = now

    order.save(
        update_fields=[
            "status",
            "cancelled_at",
            "stock_released_at",
            "updated_at",
        ]
    )

    return order


# =========================================================
# Expire Unpaid Order
# =========================================================


@transaction.atomic
def expire_unpaid_order(
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    # فقط Order منتظر پرداخت.
    if (
        order.status
        != Order.Status.PENDING_PAYMENT
    ):

        return order

    # پرداخت موفق هرگز Expire نمی‌شود.
    if (
        order.payment_status
        == Order.PaymentStatus.PAID
    ):

        return order

    # -------------------------------------------------
    # IMPORTANT
    # -------------------------------------------------
    #
    # Payment در حال بررسی Provider است.
    #
    # فعلاً آن را Expire نمی‌کنیم تا زمانی که
    # Payment Reconciliation را اضافه کنیم.
    # -------------------------------------------------

    if (
        order.payment_status
        == Order.PaymentStatus.PENDING
    ):

        return order

    # هنوز Deadline تمام نشده.
    if (
        order.expires_at
        > timezone.now()
    ):

        return order

    # -------------------------------------------------
    # Release Stock
    # -------------------------------------------------

    _release_order_stock(
        order
    )

    # -------------------------------------------------
    # Revoke Discount Usage
    # -------------------------------------------------

    if order.discount_id:

        try:

            revoke_discount_usage(
                order.order_number
            )

        except DiscountValidationError:

            # اگر Usage به هر دلیلی وجود نداشت،
            # Expire Order نباید متوقف شود.
            pass

    # -------------------------------------------------
    # Expire
    # -------------------------------------------------

    order.status = (
        Order.Status.EXPIRED
    )

    order.save(
        update_fields=[
            "status",
            "stock_released_at",
            "updated_at",
        ]
    )

    return order


# =========================================================
# Mark Order Paid
# =========================================================


@transaction.atomic
def mark_order_paid(
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    # Verify موفق دوباره نباید
    # وضعیت Order را خراب کند.
    if (
        order.payment_status
        == Order.PaymentStatus.PAID
    ):

        return order

    if order.status in {
        Order.Status.CANCELLED,
        Order.Status.EXPIRED,
    }:

        raise InvalidOrderTransitionError(
            "این سفارش دیگر قابل پرداخت نیست."
        )

    now = timezone.now()

    order.payment_status = (
        Order.PaymentStatus.PAID
    )

    order.status = (
        Order.Status.PROCESSING
    )

    order.paid_at = now

    order.save(
        update_fields=[
            "payment_status",
            "status",
            "paid_at",
            "updated_at",
        ]
    )

    return order


# =========================================================
# Operational Status
# =========================================================


@transaction.atomic
def mark_order_packing(
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    if (
        order.payment_status
        != Order.PaymentStatus.PAID
    ):

        raise InvalidOrderTransitionError(
            "سفارش پرداخت‌نشده "
            "قابل بسته‌بندی نیست."
        )

    if (
        order.status
        != Order.Status.PROCESSING
    ):

        raise InvalidOrderTransitionError(
            "وضعیت فعلی سفارش "
            "اجازه بسته‌بندی را نمی‌دهد."
        )

    order.status = (
        Order.Status.PACKING
    )

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return order


@transaction.atomic
def mark_order_shipped(
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    if (
        order.status
        != Order.Status.PACKING
    ):

        raise InvalidOrderTransitionError(
            "فقط سفارش در حال بسته‌بندی "
            "قابل ارسال است."
        )

    order.status = (
        Order.Status.SHIPPED
    )

    order.shipped_at = (
        timezone.now()
    )

    order.save(
        update_fields=[
            "status",
            "shipped_at",
            "updated_at",
        ]
    )

    return order


@transaction.atomic
def mark_order_delivered(
    order,
):

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=order.pk
        )
    )

    if (
        order.status
        != Order.Status.SHIPPED
    ):

        raise InvalidOrderTransitionError(
            "فقط سفارش ارسال‌شده "
            "قابل تحویل است."
        )

    order.status = (
        Order.Status.DELIVERED
    )

    order.delivered_at = (
        timezone.now()
    )

    order.save(
        update_fields=[
            "status",
            "delivered_at",
            "updated_at",
        ]
    )

    return order