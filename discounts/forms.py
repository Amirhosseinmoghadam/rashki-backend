from django import forms

from .models import DiscountCode


# =========================================================
# Discount Code Admin Form
# =========================================================


class DiscountCodeAdminForm(
    forms.ModelForm
):

    class Meta:

        model = DiscountCode

        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        scope = cleaned_data.get(
            "scope"
        )

        products = cleaned_data.get(
            "products"
        )

        categories = cleaned_data.get(
            "categories"
        )

        # ---------------------------------------------
        # All Products
        # ---------------------------------------------

        if scope == DiscountCode.Scope.ALL:

            cleaned_data[
                "products"
            ] = DiscountCode.products.field.remote_field.model.objects.none()

            cleaned_data[
                "categories"
            ] = DiscountCode.categories.field.remote_field.model.objects.none()

        # ---------------------------------------------
        # Products
        # ---------------------------------------------

        elif (
            scope
            == DiscountCode.Scope.PRODUCTS
        ):

            if not products:

                self.add_error(
                    "products",
                    (
                        "حداقل یک محصول "
                        "انتخاب کنید."
                    ),
                )

            cleaned_data[
                "categories"
            ] = DiscountCode.categories.field.remote_field.model.objects.none()

        # ---------------------------------------------
        # Categories
        # ---------------------------------------------

        elif (
            scope
            == DiscountCode.Scope.CATEGORIES
        ):

            if not categories:

                self.add_error(
                    "categories",
                    (
                        "حداقل یک دسته‌بندی "
                        "انتخاب کنید."
                    ),
                )

            cleaned_data[
                "products"
            ] = DiscountCode.products.field.remote_field.model.objects.none()

        return cleaned_data
