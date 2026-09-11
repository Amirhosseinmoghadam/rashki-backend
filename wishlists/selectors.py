from django.db.models import Q, Prefetch

from categories.models import Category

from products.models import (
    Product,
    ProductImage,
)

from .models import WishlistItem


# =========================================================
# Public Category IDs
# =========================================================


def get_public_category_ids():
    """
    فقط Categoryهایی را برمی‌گرداند که:

    - خود Category فعال باشد.
    - تمام Parentهای آن نیز فعال باشند.

    این رفتار با Public Product API هماهنگ است.
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

    result_cache = {}

    def is_visible(
        category,
        path=None,
    ):

        if category.id in result_cache:

            return result_cache[
                category.id
            ]

        path = path or set()

        # محافظت در برابر Cycle احتمالی.
        if category.id in path:

            result_cache[
                category.id
            ] = False

            return False

        if not category.is_active:

            result_cache[
                category.id
            ] = False

            return False

        if category.parent_id is None:

            result_cache[
                category.id
            ] = True

            return True

        parent = category_map.get(
            category.parent_id
        )

        if parent is None:

            result_cache[
                category.id
            ] = False

            return False

        result = is_visible(
            parent,
            path | {
                category.id,
            },
        )

        result_cache[
            category.id
        ] = result

        return result

    return [
        category.id
        for category in categories
        if is_visible(category)
    ]


# =========================================================
# Public Products
# =========================================================


def get_public_products_queryset():
    """
    Productهایی که در بخش عمومی سایت
    قابل مشاهده هستند.

    Product باید:
    - Active باشد.
    - Category فعال داشته باشد.
    - اگر Brand دارد، Brand فعال باشد.
    """

    public_category_ids = (
        get_public_category_ids()
    )

    return (
        Product.objects
        .filter(
            status=Product.Status.ACTIVE,
            category_id__in=(
                public_category_ids
            ),
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
    )


# =========================================================
# User Wishlist
# =========================================================


def get_user_wishlist_queryset(
    user,
):
    """
    Wishlist عمومی و قابل نمایش User را
    به صورت Optimized دریافت می‌کند.
    """

    public_category_ids = (
        get_public_category_ids()
    )

    primary_images = (
        ProductImage.objects
        .filter(
            is_primary=True
        )
        .order_by(
            "id"
        )
    )

    return (
        WishlistItem.objects
        .filter(
            user=user,
            product__status=(
                Product.Status.ACTIVE
            ),
            product__category_id__in=(
                public_category_ids
            ),
        )
        .filter(
            Q(
                product__brand__isnull=True
            )
            |
            Q(
                product__brand__is_active=True
            )
        )
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
                    "_wishlist_primary_images"
                ),
            )
        )
        .order_by(
            "-created_at"
        )
    )