from decimal import Decimal, InvalidOperation

from django.db.models import Q, Prefetch
from django.db.models.deletion import ProtectedError

from rest_framework import (
    status,
    viewsets,
)
from rest_framework.exceptions import (
    ValidationError,
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
)
from rest_framework.response import Response

from categories.models import Category

from products.models import (
    Product,
    ProductImage,
    ProductAttribute,
    ProductAttributeOption,
)
from utils.pagination import DefaultPagination

from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ProductImageWriteSerializer,
    ProductAttributeReferenceSerializer,
)

from utils.normalizers import (
    normalize_digits,
    normalize_single_line_text,
)
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from drf_spectacular.utils import extend_schema_view
from .openapi.schema import (
    product_list_view_schema,
    product_detail_view_schema,
    product_create_view_schema,
    product_update_view_schema,
    product_partial_update_view_schema,
    product_delete_view_schema,

    product_image_list_view_schema,
    product_image_detail_view_schema,
    product_image_create_view_schema,
    product_image_update_view_schema,
    product_image_partial_update_view_schema,
    product_image_delete_view_schema,

    product_attribute_list_view_schema,
    product_attribute_detail_view_schema,
)
# =========================================================
# Helpers
# =========================================================


def parse_positive_int(
    value,
    field_name,
):

    if value in (
        None,
        "",
    ):
        return None

    value = normalize_digits(
        value
    )

    try:

        value = int(value)

    except (
        TypeError,
        ValueError,
    ):

        raise ValidationError(
            {
                field_name: (
                    "مقدار باید عدد صحیح باشد."
                )
            }
        )

    if value < 0:

        raise ValidationError(
            {
                field_name: (
                    "مقدار نمی‌تواند منفی باشد."
                )
            }
        )

    return value


def parse_decimal(
    value,
    field_name,
):

    if value in (
        None,
        "",
    ):
        return None

    value = normalize_digits(
        value
    )

    try:

        value = Decimal(
            str(value)
        )

    except InvalidOperation:

        raise ValidationError(
            {
                field_name: (
                    "مقدار عددی معتبر نیست."
                )
            }
        )

    return value


def get_public_category_ids():

    """
    ID تمام Categoryهایی که خودشان و
    تمام والدهایشان Active هستند.
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

        visible = is_visible(
            parent,
            path | {
                category.id
            },
        )

        cache[
            category.id
        ] = visible

        return visible

    return [
        category.id
        for category in categories
        if is_visible(category)
    ]


def get_category_with_descendants(
    category_id,
):

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

    result = []

    stack = [
        category_id
    ]

    visited = set()

    while stack:

        current = stack.pop()

        if current in visited:
            continue

        visited.add(
            current
        )

        result.append(
            current
        )

        stack.extend(
            children_map.get(
                current,
                [],
            )
        )

    return result


# =========================================================
# Product ViewSet
# =========================================================


class ProductViewSet(
    viewsets.ModelViewSet
):

    # از Pagination پیش‌فرض DRF/Core استفاده می‌کنیم.

    # =====================================================
    # Permission
    # =====================================================

    def get_permissions(self):

        if self.action in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:

            return [
                IsAdminUser(),
            ]

        return [
            AllowAny(),
        ]

    # =====================================================
    # QuerySet
    # =====================================================

    def get_queryset(self):

        queryset = (
            Product.objects
            .select_related(
                "category",
                "brand",
            )
        )

        # -------------------------------------------------
        # Public Visibility
        # -------------------------------------------------

        if self.action in {
            "list",
            "retrieve",
        }:

            public_category_ids = (
                get_public_category_ids()
            )

            queryset = queryset.filter(
                status=Product.Status.ACTIVE,
                category_id__in=(
                    public_category_ids
                ),
            ).filter(
                Q(
                    brand__isnull=True
                )
                |
                Q(
                    brand__is_active=True
                )
            )

        # -------------------------------------------------
        # Prefetch
        # -------------------------------------------------

        queryset = queryset.prefetch_related(
            Prefetch(
                "images",
                queryset=(
                    ProductImage.objects
                    .order_by(
                        "sort_order",
                        "id",
                    )
                ),
            )
        )

        if self.action == "retrieve":

            queryset = queryset.prefetch_related(
                "attribute_values__attribute__options",
                "attribute_values__option",
                "compatibilities__motorcycle__brand",
                "relations__related_product__images",
            )

        # -------------------------------------------------
        # Filters
        # -------------------------------------------------

        if self.action == "list":

            queryset = self._apply_filters(
                queryset
            )

        return queryset

    # =====================================================
    # Filters
    # =====================================================

    def _apply_filters(
        self,
        queryset,
    ):

        params = (
            self.request.query_params
        )

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        category_id = parse_positive_int(
            params.get("category"),
            "category",
        )

        if category_id is not None:

            category_ids = (
                get_category_with_descendants(
                    category_id
                )
            )

            queryset = queryset.filter(
                category_id__in=(
                    category_ids
                )
            )

        # -------------------------------------------------
        # Brand
        # -------------------------------------------------

        brand_id = parse_positive_int(
            params.get("brand"),
            "brand",
        )

        if brand_id is not None:

            queryset = queryset.filter(
                brand_id=brand_id
            )

        # -------------------------------------------------
        # Motorcycle
        # -------------------------------------------------

        motorcycle_id = parse_positive_int(
            params.get(
                "motorcycle"
            ),
            "motorcycle",
        )

        if motorcycle_id is not None:

            queryset = queryset.filter(
                compatibilities__motorcycle_id=(
                    motorcycle_id
                )
            )

        # -------------------------------------------------
        # Price
        # -------------------------------------------------

        min_price = parse_positive_int(
            params.get(
                "min_price"
            ),
            "min_price",
        )

        if min_price is not None:

            queryset = queryset.filter(
                current_price_toman__gte=(
                    min_price
                )
            )

        max_price = parse_positive_int(
            params.get(
                "max_price"
            ),
            "max_price",
        )

        if max_price is not None:

            queryset = queryset.filter(
                current_price_toman__lte=(
                    max_price
                )
            )

        # -------------------------------------------------
        # Stock
        # -------------------------------------------------

        in_stock = params.get(
            "in_stock"
        )

        if in_stock is not None:

            in_stock = (
                str(in_stock)
                .strip()
                .lower()
            )

            if in_stock in {
                "1",
                "true",
                "yes",
            }:

                queryset = queryset.filter(
                    stock_quantity__gt=0
                )

            elif in_stock in {
                "0",
                "false",
                "no",
            }:

                queryset = queryset.filter(
                    stock_quantity=0
                )

            else:

                raise ValidationError(
                    {
                        "in_stock": (
                            "مقدار باید true "
                            "یا false باشد."
                        )
                    }
                )

        # -------------------------------------------------
        # Featured
        # -------------------------------------------------

        featured = params.get(
            "featured"
        )

        if featured is not None:

            featured = (
                str(featured)
                .strip()
                .lower()
            )

            if featured in {
                "1",
                "true",
                "yes",
            }:

                queryset = queryset.filter(
                    is_featured=True
                )

            elif featured in {
                "0",
                "false",
                "no",
            }:

                queryset = queryset.filter(
                    is_featured=False
                )

        # -------------------------------------------------
        # Search
        # -------------------------------------------------

        search = params.get(
            "search"
        )

        if search:

            search = (
                normalize_single_line_text(
                    normalize_digits(
                        search
                    )
                )
            )

            queryset = queryset.filter(
                Q(
                    name__icontains=search
                )
                |
                Q(
                    sku__icontains=search
                )
                |
                Q(
                    manufacturer_part_number__icontains=search
                )
                |
                Q(
                    oem_code__icontains=search
                )
                |
                Q(
                    barcode__icontains=search
                )
                |
                Q(
                    search_keywords__icontains=search
                )
                |
                Q(
                    brand__name__icontains=search
                )
                |
                Q(
                    category__name__icontains=search
                )
                |
                Q(
                    compatibilities__motorcycle__name__icontains=search
                )
                |
                Q(
                    compatibilities__motorcycle__brand__name__icontains=search
                )
            )

        # -------------------------------------------------
        # Dynamic Attributes
        #
        # Examples:
        #
        # ?attr_position=front
        #
        # ?attr_link-count_min=100
        # ?attr_link-count_max=130
        # -------------------------------------------------

        queryset = self._apply_attribute_filters(
            queryset,
            params,
        )

        # -------------------------------------------------
        # Ordering
        # -------------------------------------------------

        ordering = params.get(
            "ordering",
            "newest",
        )

        ordering_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "price_asc": (
                "current_price_toman"
            ),
            "price_desc": (
                "-current_price_toman"
            ),
            "name": "name",
        }

        queryset = queryset.order_by(
            ordering_map.get(
                ordering,
                "-created_at",
            )
        )

        return queryset.distinct()

    # =====================================================
    # Attribute Filters
    # =====================================================

    def _apply_attribute_filters(
        self,
        queryset,
        params,
    ):

        for key in params.keys():

            if not key.startswith(
                "attr_"
            ):
                continue

            raw = params.get(
                key
            )

            if raw in (
                None,
                "",
            ):
                continue

            attribute_key = key[
                len("attr_"):
            ]

            lookup = "exact"

            if attribute_key.endswith(
                "_min"
            ):

                lookup = "min"

                attribute_slug = (
                    attribute_key[:-4]
                )

            elif attribute_key.endswith(
                "_max"
            ):

                lookup = "max"

                attribute_slug = (
                    attribute_key[:-4]
                )

            else:

                attribute_slug = (
                    attribute_key
                )

            attribute = (
                ProductAttribute.objects
                .filter(
                    slug=attribute_slug,
                    is_active=True,
                    is_filterable=True,
                )
                .first()
            )

            if attribute is None:

                raise ValidationError(
                    {
                        key: (
                            "ویژگی فیلتر "
                            "معتبر نیست."
                        )
                    }
                )

            # ---------------------------------------------
            # Number
            # ---------------------------------------------

            if (
                attribute.data_type
                == ProductAttribute.DataType.NUMBER
            ):

                number = parse_decimal(
                    raw,
                    key,
                )

                if lookup == "min":

                    queryset = queryset.filter(
                        attribute_values__attribute=(
                            attribute
                        ),
                        attribute_values__value_number__gte=(
                            number
                        ),
                    )

                elif lookup == "max":

                    queryset = queryset.filter(
                        attribute_values__attribute=(
                            attribute
                        ),
                        attribute_values__value_number__lte=(
                            number
                        ),
                    )

                else:

                    queryset = queryset.filter(
                        attribute_values__attribute=(
                            attribute
                        ),
                        attribute_values__value_number=(
                            number
                        ),
                    )

            # ---------------------------------------------
            # Choice
            # ---------------------------------------------

            elif (
                attribute.data_type
                == ProductAttribute.DataType.CHOICE
            ):

                if lookup != "exact":

                    raise ValidationError(
                        {
                            key: (
                                "برای ویژگی انتخابی "
                                "min/max معتبر نیست."
                            )
                        }
                    )

                queryset = queryset.filter(
                    attribute_values__attribute=(
                        attribute
                    ),
                    attribute_values__option__slug=(
                        raw
                    ),
                )

            # ---------------------------------------------
            # Boolean
            # ---------------------------------------------

            elif (
                attribute.data_type
                == ProductAttribute.DataType.BOOLEAN
            ):

                boolean_value = (
                    str(raw)
                    .strip()
                    .lower()
                )

                if boolean_value in {
                    "1",
                    "true",
                    "yes",
                }:

                    boolean_value = True

                elif boolean_value in {
                    "0",
                    "false",
                    "no",
                }:

                    boolean_value = False

                else:

                    raise ValidationError(
                        {
                            key: (
                                "مقدار باید true "
                                "یا false باشد."
                            )
                        }
                    )

                queryset = queryset.filter(
                    attribute_values__attribute=(
                        attribute
                    ),
                    attribute_values__value_boolean=(
                        boolean_value
                    ),
                )

            # ---------------------------------------------
            # Text
            # ---------------------------------------------

            else:

                queryset = queryset.filter(
                    attribute_values__attribute=(
                        attribute
                    ),
                    attribute_values__value_text__iexact=(
                        raw
                    ),
                )

        return queryset

    # =====================================================
    # Serializer
    # =====================================================

    def get_serializer_class(self):

        if self.action == "list":

            return ProductListSerializer

        if self.action == "retrieve":

            return ProductDetailSerializer

        return ProductCreateUpdateSerializer

    # =====================================================
    # List
    # =====================================================
    @product_list_view_schema
    def list(
        self,
        request,
        *args,
        **kwargs,
    ):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(
            queryset
        )

        if page is not None:

            serializer = ProductListSerializer(
                page,
                many=True,
                context=(
                    self.get_serializer_context()
                ),
            )

            return Response(
                {
                    "success": True,
                    "message": (
                        "لیست محصولات با موفقیت "
                        "دریافت شد."
                    ),
                    "data": {
                        "count": (
                            self.paginator.page
                            .paginator.count
                        ),
                        "next": (
                            self.paginator
                            .get_next_link()
                        ),
                        "previous": (
                            self.paginator
                            .get_previous_link()
                        ),
                        "results": (
                            serializer.data
                        ),
                    },
                },
                status=status.HTTP_200_OK,
            )

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context=(
                self.get_serializer_context()
            ),
        )

        return Response(
            {
                "success": True,
                "message": (
                    "لیست محصولات با موفقیت "
                    "دریافت شد."
                ),
                "count": len(
                    serializer.data
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # Retrieve
    # =====================================================
    @product_detail_view_schema
    def retrieve(
        self,
        request,
        *args,
        **kwargs,
    ):

        product = self.get_object()

        serializer = (
            ProductDetailSerializer(
                product,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت "
                    "دریافت شد."
                ),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # Create
    # =====================================================
    @product_create_view_schema
    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = (
            ProductCreateUpdateSerializer(
                data=request.data,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.save()

        response_serializer = (
            ProductDetailSerializer(
                Product.objects
                .select_related(
                    "category",
                    "brand",
                )
                .prefetch_related(
                    "images",
                    "attribute_values__attribute__options",
                    "attribute_values__option",
                    "compatibilities__motorcycle__brand",
                    "relations__related_product__images",
                )
                .get(
                    pk=product.pk
                ),
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت ایجاد شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    # =====================================================
    # Update
    # =====================================================
    @product_update_view_schema
    def update(
        self,
        request,
        *args,
        **kwargs,
    ):

        partial = kwargs.pop(
            "partial",
            False,
        )

        product = self.get_object()

        serializer = (
            ProductCreateUpdateSerializer(
                product,
                data=request.data,
                partial=partial,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.save()

        response_product = (
            Product.objects
            .select_related(
                "category",
                "brand",
            )
            .prefetch_related(
                "images",
                "attribute_values__attribute__options",
                "attribute_values__option",
                "compatibilities__motorcycle__brand",
                "relations__related_product__images",
            )
            .get(
                pk=product.pk
            )
        )

        response_serializer = (
            ProductDetailSerializer(
                response_product,
                context=(
                    self.get_serializer_context()
                ),
            )
        )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت "
                    "بروزرسانی شد."
                ),
                "data": (
                    response_serializer.data
                ),
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # PATCH
    # =====================================================
    @product_partial_update_view_schema
    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):

        kwargs["partial"] = True

        return self.update(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # Delete
    # =====================================================
    @product_delete_view_schema
    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        product = self.get_object()

        try:

            product.delete()

        except ProtectedError:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این محصول به اطلاعات "
                        "دیگری وابسته است و "
                        "قابل حذف نیست."
                    ),
                    "errors": None,
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        return Response(
            {
                "success": True,
                "message": (
                    "محصول با موفقیت حذف شد."
                ),
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# Product Image Admin API
# =========================================================

@extend_schema_view(
    list=product_image_list_view_schema,
    retrieve=product_image_detail_view_schema,
    create=product_image_create_view_schema,
    update=product_image_update_view_schema,
    partial_update=(
        product_image_partial_update_view_schema
    ),
    destroy=product_image_delete_view_schema,
)
class ProductImageViewSet(
    viewsets.ModelViewSet
):

    permission_classes = [
        IsAdminUser,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]
    pagination_class = DefaultPagination

    queryset = (
        ProductImage.objects
        .select_related(
            "product"
        )
        .order_by(
            "product_id",
            "sort_order",
            "id",
        )
    )

    def get_serializer_class(self):

        if self.action in {
            "list",
            "retrieve",
        }:

            return (
                ProductImageSerializer
            )

        return (
            ProductImageWriteSerializer
        )


# =========================================================
# Product Attribute Public API
# =========================================================

@extend_schema_view(
    list=product_attribute_list_view_schema,
    retrieve=product_attribute_detail_view_schema,
)
class ProductAttributeViewSet(
    viewsets.ReadOnlyModelViewSet
):

    permission_classes = [
        AllowAny,
    ]

    pagination_class = None

    serializer_class = (
        ProductAttributeReferenceSerializer
    )

    def get_queryset(self):

        queryset = (
            ProductAttribute.objects
            .filter(
                is_active=True
            )
            .prefetch_related(
                Prefetch(
                    "options",
                    queryset=(
                        ProductAttributeOption.objects
                        .filter(
                            is_active=True
                        )
                        .order_by(
                            "sort_order",
                            "value",
                        )
                    ),
                )
            )
        )

        category_id = (
            self.request
            .query_params
            .get("category")
        )

        if category_id:

            category_id = parse_positive_int(
                category_id,
                "category",
            )

            try:

                category = (
                    Category.objects.get(
                        pk=category_id
                    )
                )

            except Category.DoesNotExist:

                return queryset.none()

            ids = []

            current = category

            visited = set()

            while current:

                if current.pk in visited:
                    break

                visited.add(
                    current.pk
                )

                ids.append(
                    current.pk
                )

                current = current.parent

            queryset = queryset.filter(
                categories__id__in=ids
            )

        return (
            queryset
            .distinct()
            .order_by(
                "sort_order",
                "name",
            )
        )