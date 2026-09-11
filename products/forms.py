from django import forms

from pricing.services import (
    PricingError,
    calculate_product_price,
)

from .models import Product


class ProductAdminForm(
    forms.ModelForm
):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        pricing_mode = cleaned_data.get(
            "pricing_mode"
        )

        status = cleaned_data.get(
            "status"
        )

        # مقادیر فرم را روی instance موقت قرار می‌دهیم
        # تا Pricing Engine دقیقاً همان اطلاعات جدید را ببیند.
        for field_name in (
            "pricing_mode",
            "base_price_usd",
            "base_price_toman",
            "markup_percent",
            "fixed_cost_toman",
            "is_price_locked",
        ):
            if field_name in cleaned_data:
                setattr(
                    self.instance,
                    field_name,
                    cleaned_data[field_name],
                )

        try:
            result = calculate_product_price(
                self.instance
            )

        except PricingError as exc:

            # Draft می‌تواند بدون قیمت نهایی باقی بماند.
            if (
                status
                != Product.Status.ACTIVE
            ):
                self._price_result = None
                return cleaned_data

            raise forms.ValidationError(
                str(exc)
            ) from exc

        self._price_result = result

        return cleaned_data