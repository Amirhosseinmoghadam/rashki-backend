from django.db.models import (
    Prefetch,
    Q,
)

from categories.models import Category

from products.models import (
    Product,
    ProductImage,
)

from .models import (
    Cart,
    CartItem,
)


# =========================================================
# Public Category IDs
# =========================================================


def get_public_category_ids():
    """
    Categoryهایی که خودشان و
    تمام Parentهایشان Active هستند.
    """

    categories = list(
        Category.objects.all().only(
            "id",
            "parent_id",
            "is_active",
        )
    )

    category_map = {
        category.id: category
        for category in categories
    }

    cache = {}

    def is_visible(
        category,
        path=None,
    ):

        if category.id in cache:

            return cache[
                category.id
            ]

        path = path or set()

        if category.id in path:

            cache[
                category.id
            ] = False

            return False

        if not category.is_active:

            cache[
                category.id
            ] = False

            return False

        if category.parent_id is None:

            cache[
                category.id
            ] = True

            return True

        parent = category_map.get(
            category.parent_id
        )

        if parent is None:

            cache[
                category.id
            ] = False

            return False

        result = is_visible(
            parent,
            path | {
                category.id
            },
        )

        cache[
            category.id
        ] = result

        return result

    return [
        category.id
        for category in categories
        if is_visible(category)
    ]


# =========================================================
# Purchasable Products
# =========================================================


def get_purchasable_products_queryset():
    """
    Productهایی که در حال حاضر
    امکان خریدشان وجود دارد.

    Product باید:

    - Active باشد.
    - Category قابل نمایش داشته باشد.
    - Brand فعال یا Null داشته باشد.
    - قیمت نهایی داشته باشد.

    Stock در Service بررسی می‌شود چون
    Quantity نیز در آنجا اهمیت دارد.
    """

    return (
        Product.objects
        .filter(
            status=Product.Status.ACTIVE,
            category_id__in=(
                get_public_category_ids()
            ),
            current_price_toman__isnull=False,
        )
        .filter(
            Q(
                brand__isnull=True
            )
            |
            Q(
                brand__is_active=True
            )
        )
        .select_related(
            "category",
            "brand",
        )
    )


# =========================================================
# Optimized Cart
# =========================================================


def get_cart_queryset():
    """
    QuerySet بهینه Cart برای نمایش API.
    """

    primary_images = (
        ProductImage.objects
        .filter(
            is_primary=True
        )
        .order_by(
            "id"
        )
    )

    cart_items = (
        CartItem.objects
        .select_related(
            "product",
            "product__category",
            "product__brand",
        )
        .prefetch_related(
            Prefetch(
                "product__images",
                queryset=primary_images,
                to_attr=(
                    "_cart_primary_images"
                ),
            )
        )
        .order_by(
            "created_at",
            "id",
        )
    )

    return (
        Cart.objects
        .select_related(
            "user",
            "applied_discount",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=cart_items,
            )
        )
    )