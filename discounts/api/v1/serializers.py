import re

from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema_field,
)

from categories.models import Category
from products.models import Product

from discounts.models import (
    DiscountCode,
    DiscountUsage,
)

from discounts.services import (
    normalize_discount_code,
)


# =========================================================
# References
# =========================================================


class DiscountProductReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "sku",
        ]

        read_only_fields = fields


class DiscountCategoryReferenceSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Category

        fields = [
            "id",
            "name",
            "slug",
        ]

        read_only_fields = fields


# =========================================================
# Discount Code Admin
# =========================================================


class DiscountCodeSerializer(
    serializers.ModelSerializer
):

    products = (
        DiscountProductReferenceSerializer(
            many=True,
            read_only=True,
        )
    )

    categories = (
        DiscountCategoryReferenceSerializer(
            many=True,
            read_only=True,
        )
    )

    product_ids = (
        serializers.PrimaryKeyRelatedField(
            source="products",
            queryset=Product.objects.all(),
            many=True,
            required=False,
            write_only=True,
        )
    )

    category_ids = (
        serializers.PrimaryKeyRelatedField(
            source="categories",
            queryset=Category.objects.all(),
            many=True,
            required=False,
            write_only=True,
        )
    )

    usage_count = (
        serializers.SerializerMethodField()
    )

    remaining_usage = (
        serializers.SerializerMethodField()
    )

    class Meta:

        model = DiscountCode

        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "percentage",
            "fixed_amount_toman",
            "minimum_order_toman",
            "maximum_discount_toman",
            "scope",
            "products",
            "product_ids",
            "categories",
            "category_ids",
            "start_at",
            "end_at",
            "usage_limit",
            "usage_limit_per_user",
            "usage_count",
            "remaining_usage",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "usage_count",
            "remaining_usage",
            "created_at",
            "updated_at",
        ]

    # =====================================================
    # Code
    # =====================================================

    def validate_code(
        self,
        value,
    ):

        value = normalize_discount_code(
            value
        )

        # برای جلوگیری از اشتباه کاربر،
        # Promo Code را به حروف لاتین،
        # عدد، - و _ محدود می‌کنیم.
        if not re.fullmatch(
            r"[A-Z0-9_-]+",
            value,
        ):

            raise serializers.ValidationError(
                "کد تخفیف فقط می‌تواند شامل "
                "حروف انگلیسی، عدد، - و _ باشد."
            )

        queryset = (
            DiscountCode.objects.filter(
                code=value
            )
        )

        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():

            raise serializers.ValidationError(
                "این کد تخفیف قبلاً "
                "ثبت شده است."
            )

        return value

    # =====================================================
    # Object Validation
    # =====================================================

    def validate(
        self,
        attrs,
    ):

        instance = self.instance

        discount_type = attrs.get(
            "discount_type",
            (
                instance.discount_type
                if instance
                else None
            ),
        )

        percentage = attrs.get(
            "percentage",
            (
                instance.percentage
                if instance
                else None
            ),
        )

        fixed_amount = attrs.get(
            "fixed_amount_toman",
            (
                instance.fixed_amount_toman
                if instance
                else None
            ),
        )

        start_at = attrs.get(
            "start_at",
            (
                instance.start_at
                if instance
                else None
            ),
        )

        end_at = attrs.get(
            "end_at",
            (
                instance.end_at
                if instance
                else None
            ),
        )

        scope = attrs.get(
            "scope",
            (
                instance.scope
                if instance
                else DiscountCode.Scope.ALL
            ),
        )

        # ---------------------------------------------
        # Type
        # ---------------------------------------------

        if (
            discount_type
            == DiscountCode
            .DiscountType
            .PERCENTAGE
            and percentage is None
        ):

            raise serializers.ValidationError(
                {
                    "percentage": (
                        "درصد تخفیف الزامی است."
                    )
                }
            )

        if (
            discount_type
            == DiscountCode
            .DiscountType
            .FIXED_AMOUNT
            and fixed_amount is None
        ):

            raise serializers.ValidationError(
                {
                    "fixed_amount_toman": (
                        "مبلغ تخفیف الزامی است."
                    )
                }
            )

        # ---------------------------------------------
        # Date
        # ---------------------------------------------

        if (
            start_at is not None
            and end_at is not None
            and end_at <= start_at
        ):

            raise serializers.ValidationError(
                {
                    "end_at": (
                        "زمان پایان باید بعد "
                        "از زمان شروع باشد."
                    )
                }
            )

        # ---------------------------------------------
        # Scope
        # ---------------------------------------------

        products = attrs.get(
            "products"
        )

        categories = attrs.get(
            "categories"
        )

        if products is None and instance:

            products = list(
                instance.products.all()
            )

        if categories is None and instance:

            categories = list(
                instance.categories.all()
            )

        products = products or []
        categories = categories or []

        if (
            scope
            == DiscountCode.Scope.PRODUCTS
            and not products
        ):

            raise serializers.ValidationError(
                {
                    "product_ids": (
                        "حداقل یک محصول "
                        "انتخاب کنید."
                    )
                }
            )

        if (
            scope
            == DiscountCode.Scope.CATEGORIES
            and not categories
        ):

            raise serializers.ValidationError(
                {
                    "category_ids": (
                        "حداقل یک دسته‌بندی "
                        "انتخاب کنید."
                    )
                }
            )

        return attrs

    # =====================================================
    # Create
    # =====================================================

    def create(
        self,
        validated_data,
    ):

        discount = super().create(
            validated_data
        )

        self._cleanup_scope(
            discount
        )

        return discount

    # =====================================================
    # Update
    # =====================================================

    def update(
        self,
        instance,
        validated_data,
    ):

        discount = super().update(
            instance,
            validated_data,
        )

        self._cleanup_scope(
            discount
        )

        return discount

    def _cleanup_scope(
        self,
        discount,
    ):

        if (
            discount.scope
            == DiscountCode.Scope.ALL
        ):

            discount.products.clear()
            discount.categories.clear()

        elif (
            discount.scope
            == DiscountCode.Scope.PRODUCTS
        ):

            discount.categories.clear()

        elif (
            discount.scope
            == DiscountCode.Scope.CATEGORIES
        ):

            discount.products.clear()

    # =====================================================
    # Usage
    # =====================================================

    @extend_schema_field(
        serializers.IntegerField()
    )
    def get_usage_count(
        self,
        obj,
    ):

        annotated = getattr(
            obj,
            "active_usage_count",
            None,
        )

        if annotated is not None:
            return annotated

        return obj.usages.filter(
            status=(
                DiscountUsage.Status.USED
            )
        ).count()

    @extend_schema_field(
        serializers.IntegerField(
            allow_null=True
        )
    )
    def get_remaining_usage(
        self,
        obj,
    ):

        if obj.usage_limit is None:
            return None

        return max(
            0,
            obj.usage_limit
            - self.get_usage_count(obj),
        )


# =========================================================
# Validate Request
# =========================================================


class DiscountValidateItemSerializer(
    serializers.Serializer
):

    # Product ID موجود در Cart.
    product_id = serializers.IntegerField(
        min_value=1,
    )

    # تعداد Product.
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=10000,
    )


class DiscountValidateSerializer(
    serializers.Serializer
):

    code = serializers.CharField(
        max_length=50,
    )

    items = DiscountValidateItemSerializer(
        many=True,
    )

    def validate_code(
        self,
        value,
    ):

        return normalize_discount_code(
            value
        )

    def validate_items(
        self,
        value,
    ):

        if not value:

            raise serializers.ValidationError(
                "سبد خرید نمی‌تواند خالی باشد."
            )

        if len(value) > 100:

            raise serializers.ValidationError(
                "حداکثر 100 نوع محصول "
                "قابل ارسال است."
            )

        product_ids = [
            item[
                "product_id"
            ]
            for item in value
        ]

        if (
            len(product_ids)
            != len(set(product_ids))
        ):

            raise serializers.ValidationError(
                "یک Product بیش از یک بار "
                "ارسال شده است."
            )

        return value


# =========================================================
# Calculation Response
# =========================================================


class DiscountCalculationSerializer(
    serializers.Serializer
):

    code = serializers.CharField()

    discount_type = serializers.CharField()

    scope = serializers.CharField()

    subtotal_toman = serializers.IntegerField()

    eligible_subtotal_toman = (
        serializers.IntegerField()
    )

    discount_amount_toman = (
        serializers.IntegerField()
    )

    final_subtotal_toman = (
        serializers.IntegerField()
    )

    start_at = serializers.DateTimeField()

    end_at = serializers.DateTimeField(
        allow_null=True
    )