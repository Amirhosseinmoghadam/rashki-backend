from django.db.models import Q

from categories.models import Category

from products.models import Product


# =========================================================
# Public Category IDs
# =========================================================


def get_public_category_ids():

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
# Public Products
# =========================================================


def get_discount_products_queryset():

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