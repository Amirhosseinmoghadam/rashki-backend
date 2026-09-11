from __future__ import annotations

from decimal import Decimal, InvalidOperation

from shipping.models import (
    ShippingMethod,
    ShippingProviderCityMap,
    TipaxSettings,
)

from shipping.origins.selectors import (
    ShippingOriginNotConfigured,
    get_default_shipping_origin,
)
from shipping.providers.tipax_client import (
    TipaxClient,
    TipaxIndeterminateError,
    TipaxRequestError,
)
from .base import (
    BaseShippingProvider,
    ProviderQuote,
    ShippingProviderConfigurationError,
    ShippingProviderUnavailableError,
    ShippingRateNotFoundError,
)

from .tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


class TipaxProvider(BaseShippingProvider):
    """
    Provider نهایی Tipax.

    جریان کلی:

        Product
            ↓
        PackagingService
            ↓
        ShippingPackage[]
            ↓
        ShippingOrigin پیش‌فرض
            ↓
        ShippingProviderCityMap
            ↓
        Tipax GetServicesBetweenCities
            ↓
        Tipax Pricing
            ↓
        finalPrice
    """

    provider_code = ShippingMethod.Provider.TIPAX

    RATE_FIELDS = (
        "regularRate",
        "regularPlusRate",
        "expressRate",
        "sameDayExpressRate",
        "airExpressRate",
    )

    def __init__(
        self,
        *,
        client=None,
    ):
        self.client = client or TipaxClient()

    # =========================================================
    # Tipax settings
    # =========================================================

    @staticmethod
    def _get_tipax_settings():
        """
        تنظیمات اصلی Tipax را دریافت می‌کند.
        """

        settings_obj = (
            TipaxSettings.objects
            .order_by("pk")
            .first()
        )

        if settings_obj is None:
            raise ShippingProviderConfigurationError(
                "تنظیمات Tipax تعریف نشده است."
            )

        return settings_obj

    # =========================================================
    # Validate shipping method
    # =========================================================

    @classmethod
    def _validate_method(
        cls,
        method,
    ):
        if method is None:
            raise ShippingProviderConfigurationError(
                "روش ارسال مشخص نشده است."
            )

        if method.provider != cls.provider_code:
            raise ShippingProviderConfigurationError(
                "روش ارسال انتخاب‌شده متعلق به Tipax نیست."
            )

        if not method.is_active:
            raise ShippingProviderUnavailableError(
                "روش ارسال Tipax غیرفعال است."
            )

    # =========================================================
    # Validate Tipax settings
    # =========================================================

    @staticmethod
    def _validate_tipax_settings(
        settings_obj,
    ):
        required_fields = (
            "payment_type",
            "pickup_type",
            "distribution_type",
        )

        for field_name in required_fields:
            value = getattr(
                settings_obj,
                field_name,
                None,
            )

            if value in (
                None,
                "",
            ):
                raise ShippingProviderConfigurationError(
                    (
                        f"فیلد «{field_name}» "
                        "در تنظیمات Tipax تعریف نشده است."
                    )
                )

            try:
                value = int(value)

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ShippingProviderConfigurationError(
                    (
                        f"مقدار «{field_name}» "
                        "در تنظیمات Tipax معتبر نیست."
                    )
                ) from exc

            if value <= 0:
                raise ShippingProviderConfigurationError(
                    (
                        f"مقدار «{field_name}» "
                        "در تنظیمات Tipax معتبر نیست."
                    )
                )

    # =========================================================
    # Shipping origin
    # =========================================================

    @staticmethod
    def _get_origin(
        origin=None,
    ):
        """
        اگر Origin مستقیم ارسال نشده باشد،
        مبدا پیش‌فرض فعلی سایت از Admin خوانده می‌شود.
        """

        if origin is not None:
            return origin

        try:
            origin = get_default_shipping_origin()

        except ShippingOriginNotConfigured as exc:
            raise ShippingProviderConfigurationError(
                str(exc)
            ) from exc

        return origin

    # =========================================================
    # Tipax city map
    # =========================================================

    @classmethod
    def _get_tipax_city_id(
        cls,
        city,
    ):
        """
        City داخلی پروژه → cityId واقعی Tipax
        """

        if city is None:
            raise ShippingProviderConfigurationError(
                "شهر برای محاسبه ارسال مشخص نشده است."
            )

        city_map = (
            ShippingProviderCityMap.objects
            .filter(
                provider=cls.provider_code,
                city=city,
                is_active=True,
            )
            .first()
        )

        if city_map is None:
            raise ShippingProviderUnavailableError(
                (
                    f"شهر «{city.name}» "
                    "به شهرهای Tipax متصل نشده است."
                )
            )

        try:
            provider_city_id = int(
                city_map.provider_city_id
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                (
                    f"شناسه Tipax برای شهر "
                    f"«{city.name}» معتبر نیست."
                )
            ) from exc

        if provider_city_id <= 0:
            raise ShippingProviderConfigurationError(
                (
                    f"شناسه Tipax برای شهر "
                    f"«{city.name}» معتبر نیست."
                )
            )

        return provider_city_id

    # =========================================================
    # Service ID
    # =========================================================

    @staticmethod
    def _get_service_id(
        method,
        settings_obj,
    ):
        """
        اولویت:

        1. ShippingMethod.service_code
        2. TipaxSettings.default_service_id
        """

        service_code = str(
            method.service_code or ""
        ).strip()

        if service_code:
            value = service_code

        else:
            value = getattr(
                settings_obj,
                "default_service_id",
                None,
            )

        try:
            service_id = int(value)

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                "serviceId مربوط به Tipax معتبر نیست."
            ) from exc

        if service_id <= 0:
            raise ShippingProviderConfigurationError(
                "serviceId مربوط به Tipax معتبر نیست."
            )

        return service_id

    # =========================================================
    # Available services
    # =========================================================

    def _get_available_services(
        self,
        *,
        origin_city_id,
        destination_city_id,
    ):
        """
        سرویس‌های واقعی Tipax بین مبدا و مقصد.
        """

        response = (
            self.client
            .get_services_between_cities(
                source_city_id=origin_city_id,
                destination_city_id=(
                    destination_city_id
                ),
            )
        )

        if not isinstance(
            response,
            dict,
        ):
            raise ShippingProviderUnavailableError(
                (
                    "پاسخ Tipax برای سرویس‌های "
                    "بین دو شهر معتبر نیست."
                )
            )

        data = response.get("data") or {}

        if not isinstance(
            data,
            dict,
        ):
            raise ShippingProviderUnavailableError(
                (
                    "بخش data در پاسخ سرویس‌های "
                    "Tipax معتبر نیست."
                )
            )

        services = (
            data.get("serviceList")
            or []
        )

        if not isinstance(
            services,
            list,
        ):
            raise ShippingProviderUnavailableError(
                (
                    "serviceList برگشتی Tipax "
                    "معتبر نیست."
                )
            )

        return services

    # =========================================================
    # Find configured service
    # =========================================================

    @staticmethod
    def _find_service(
        *,
        services,
        service_id,
    ):
        for service in services:
            if not isinstance(
                service,
                dict,
            ):
                continue

            try:
                current_service_id = int(
                    service.get(
                        "serviceId"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if current_service_id == service_id:
                return service

        raise ShippingProviderUnavailableError(
            (
                f"سرویس Tipax با serviceId={service_id} "
                "برای مسیر انتخاب‌شده در دسترس نیست."
            )
        )

    # =========================================================
    # Validate package
    # =========================================================

    @staticmethod
    def _validate_package(
        package,
    ):
        if package is None:
            raise ShippingProviderConfigurationError(
                "Package معتبر نیست."
            )

        # -------------------------
        # Weight
        # -------------------------

        try:
            weight_grams = int(
                package.weight_grams
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                "وزن Package معتبر نیست."
            ) from exc

        if weight_grams <= 0:
            raise ShippingProviderConfigurationError(
                (
                    "وزن Package باید "
                    "بیشتر از صفر باشد."
                )
            )

        # -------------------------
        # Dimensions
        # -------------------------

        dimension_fields = (
            "length_cm",
            "width_cm",
            "height_cm",
        )

        for field_name in dimension_fields:
            value = getattr(
                package,
                field_name,
                None,
            )

            try:
                decimal_value = Decimal(
                    str(value)
                )

            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ) as exc:
                raise ShippingProviderConfigurationError(
                    (
                        f"{field_name} "
                        "برای Package معتبر نیست."
                    )
                ) from exc

            if decimal_value <= 0:
                raise ShippingProviderConfigurationError(
                    (
                        f"{field_name} "
                        "باید بیشتر از صفر باشد."
                    )
                )

        # -------------------------
        # Tipax packing
        # -------------------------

        try:
            packing_id = int(
                package.provider_packing_id
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                (
                    "packingId مربوط به "
                    "Package معتبر نیست."
                )
            ) from exc

        if packing_id <= 0:
            raise ShippingProviderConfigurationError(
                (
                    "packingId مربوط به "
                    "Package معتبر نیست."
                )
            )

        try:
            package_content_id = int(
                package.package_content_id
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                (
                    "packageContentId مربوط به "
                    "Package معتبر نیست."
                )
            ) from exc

        if package_content_id <= 0:
            raise ShippingProviderConfigurationError(
                (
                    "packageContentId مربوط به "
                    "Package معتبر نیست."
                )
            )

        try:
            pack_type = int(
                package.pack_type
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ShippingProviderConfigurationError(
                (
                    "packType مربوط به "
                    "Package معتبر نیست."
                )
            ) from exc

        if pack_type <= 0:
            raise ShippingProviderConfigurationError(
                "packType مربوط به Package معتبر نیست."
            )

        # declared_value_toman می‌تواند در مرحله
        # Packaging هنوز None باشد.
        declared_value = getattr(
            package,
            "declared_value_toman",
            None,
        )

        if declared_value is not None:
            try:
                declared_value = int(
                    declared_value
                )

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ShippingProviderConfigurationError(
                    "ارزش مرسوله Package معتبر نیست."
                ) from exc

            if declared_value <= 0:
                raise ShippingProviderConfigurationError(
                    (
                        "ارزش مرسوله Package "
                        "باید بیشتر از صفر باشد."
                    )
                )

    # =========================================================
    # Weight conversion
    # =========================================================

    @staticmethod
    def _weight_to_tipax(
        weight_grams,
    ):
        """
        وزن داخلی:
            gram

        وزن Pricing فعلی Tipax:
            kilogram

        تست Live قبلی:
            1000 gram → 1.0
        """

        weight_kg = (
            Decimal(
                str(
                    weight_grams
                )
            )
            /
            Decimal("1000")
        )

        return float(
            weight_kg
        )

    # =========================================================
    # Resolve package value
    # =========================================================

    @staticmethod
    def _resolve_package_value(
        *,
        package,
        package_count,
        fallback_package_value_toman,
    ):
        """
        ارزش هر بسته را مشخص می‌کند.

        حالت اصلی:
            package.declared_value_toman

        Fallback:
            فقط اگر یک Package داشته باشیم.

        برای چند Package هر Package باید ارزش واقعی خودش
        را از Cart calculation دریافت کرده باشد.
        """

        declared_value = getattr(
            package,
            "declared_value_toman",
            None,
        )

        if declared_value is not None:
            try:
                declared_value = int(
                    declared_value
                )

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ShippingProviderConfigurationError(
                    "ارزش مرسوله Package معتبر نیست."
                ) from exc

            if declared_value <= 0:
                raise ShippingProviderConfigurationError(
                    (
                        "ارزش مرسوله Package "
                        "باید بیشتر از صفر باشد."
                    )
                )

            return declared_value

        # فقط تک‌بسته‌ای
        if package_count == 1:
            try:
                fallback_value = int(
                    fallback_package_value_toman
                    or 0
                )

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ShippingProviderConfigurationError(
                    (
                        "ارزش کل سفارش برای "
                        "محاسبه Tipax معتبر نیست."
                    )
                ) from exc

            if fallback_value > 0:
                return fallback_value

        raise ShippingProviderConfigurationError(
            (
                "ارزش واقعی یکی از بسته‌های سفارش "
                "مشخص نشده است. برای سفارش چندبسته‌ای "
                "باید ارزش هر Package از محاسبات Cart "
                "به PackagingService ارسال شود."
            )
        )

    # =========================================================
    # Build pricing payload
    # =========================================================

    def _build_pricing_payload(
        self,
        *,
        packages,
        origin_city_id,
        destination_city_id,
        service_id,
        settings_obj,
        fallback_package_value_toman=0,
    ):
        """
        ساخت Payload واقعی Pricing Tipax.

        ساختار واقعی:

            {
                "packageInputs": [
                    {...},
                    {...}
                ],
                "discountCode": ""
            }
        """

        packages = list(
            packages
        )

        if not packages:
            raise ShippingProviderConfigurationError(
                (
                    "هیچ Packageای برای "
                    "محاسبه Tipax وجود ندارد."
                )
            )

        package_count = len(
            packages
        )

        package_inputs = []

        for package in packages:
            self._validate_package(
                package
            )

            declared_value_toman = (
                self._resolve_package_value(
                    package=package,
                    package_count=package_count,
                    fallback_package_value_toman=(
                        fallback_package_value_toman
                    ),
                )
            )

            package_input = {
                "origin": {
                    "cityId": int(
                        origin_city_id
                    ),
                },

                "destination": {
                    "cityId": int(
                        destination_city_id
                    ),
                },

                "weight": (
                    self._weight_to_tipax(
                        package.weight_grams
                    )
                ),

                "packageValue": (
                    self.client
                    .to_tipax_amount(
                        declared_value_toman
                    )
                ),

                "length": float(
                    package.length_cm
                ),

                "width": float(
                    package.width_cm
                ),

                "height": float(
                    package.height_cm
                ),

                "packingId": int(
                    package.provider_packing_id
                ),

                "packageContentId": int(
                    package.package_content_id
                ),

                "packType": int(
                    package.pack_type
                ),

                "paymentType": int(
                    settings_obj.payment_type
                ),

                "pickupType": int(
                    settings_obj.pickup_type
                ),

                "distributionType": int(
                    settings_obj.distribution_type
                ),

                "serviceId": int(
                    service_id
                ),

                "parcelBookId": None,
            }

            package_inputs.append(
                package_input
            )

        return {
            "packageInputs": package_inputs,
            "discountCode": "",
        }

    # =========================================================
    # Find rate
    # =========================================================

    @classmethod
    def _find_rate(
        cls,
        *,
        package_result,
        service_id,
    ):
        """
        Rate صحیح را براساس serviceId پیدا می‌کند.

        برای سرویس فعلی ما معمولاً:
            regularRate
        """

        for rate_field in cls.RATE_FIELDS:
            rate = package_result.get(
                rate_field
            )

            if not isinstance(
                rate,
                dict,
            ):
                continue

            try:
                rate_service_id = int(
                    rate.get(
                        "serviceId"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if rate_service_id == service_id:
                return (
                    rate_field,
                    rate,
                )

        raise ShippingRateNotFoundError(
            (
                f"Rate مربوط به serviceId={service_id} "
                "در پاسخ Tipax پیدا نشد."
            )
        )

    # =========================================================
    # Parse pricing response
    # =========================================================

    def _parse_pricing_result(
        self,
        *,
        pricing_result,
        packages,
        service_id,
        fallback_package_value_toman=0,
    ):
        """
        پاسخ چندبسته‌ای Tipax را Parse می‌کند.

        finalPrice هر Package جدا گرفته شده
        و سپس مجموع می‌شود.
        """

        packages = list(
            packages
        )

        if not isinstance(
            pricing_result,
            list,
        ):
            raise ShippingRateNotFoundError(
                (
                    "پاسخ Pricing تیپاکس "
                    "باید از نوع list باشد."
                )
            )

        if not pricing_result:
            raise ShippingRateNotFoundError(
                "Tipax هیچ قیمت ارسالی برنگرداند."
            )

        if len(
            pricing_result
        ) != len(
            packages
        ):
            raise ShippingRateNotFoundError(
                (
                    "تعداد پاسخ‌های Pricing تیپاکس "
                    "با تعداد Packageهای ارسال‌شده "
                    "برابر نیست."
                )
            )

        total_amount_toman = 0

        package_breakdown = []

        package_count = len(
            packages
        )

        for index, (
            package_result,
            package,
        ) in enumerate(
            zip(
                pricing_result,
                packages,
            ),
            start=1,
        ):
            if not isinstance(
                package_result,
                dict,
            ):
                raise ShippingRateNotFoundError(
                    (
                        f"پاسخ Pricing برای Package "
                        f"شماره {index} معتبر نیست."
                    )
                )

            rate_field, rate = (
                self._find_rate(
                    package_result=(
                        package_result
                    ),
                    service_id=service_id,
                )
            )

            final_price = rate.get(
                "finalPrice"
            )

            if final_price is None:
                raise ShippingRateNotFoundError(
                    (
                        f"finalPrice برای Package "
                        f"شماره {index} در پاسخ "
                        "Tipax وجود ندارد."
                    )
                )

            try:
                amount_toman = (
                    self.client.to_toman(
                        final_price
                    )
                )

            except (
                TypeError,
                ValueError,
                InvalidOperation,
            ) as exc:
                raise ShippingRateNotFoundError(
                    (
                        f"finalPrice مربوط به Package "
                        f"شماره {index} معتبر نیست."
                    )
                ) from exc

            declared_value_toman = (
                self._resolve_package_value(
                    package=package,
                    package_count=package_count,
                    fallback_package_value_toman=(
                        fallback_package_value_toman
                    ),
                )
            )

            total_amount_toman += (
                amount_toman
            )

            package_breakdown.append(
                {
                    "package_index": index,

                    "box_number": (
                        package.box_number
                    ),

                    "packing_id": (
                        package.provider_packing_id
                    ),

                    "packing_title": (
                        package
                        .provider_packing_title
                    ),

                    "pack_type": (
                        package.pack_type
                    ),

                    "package_content_id": (
                        package
                        .package_content_id
                    ),

                    "parcel_type_id": (
                        package.parcel_type_id
                    ),

                    "weight_grams": (
                        package.weight_grams
                    ),

                    "dimensions": {
                        "length_cm": str(
                            package.length_cm
                        ),
                        "width_cm": str(
                            package.width_cm
                        ),
                        "height_cm": str(
                            package.height_cm
                        ),
                    },

                    "declared_value_toman": (
                        declared_value_toman
                    ),

                    "items": [
                        {
                            "product_id": (
                                item.product_id
                            ),

                            "product_name": (
                                item.product_name
                            ),

                            "quantity": (
                                item.quantity
                            ),

                            "weight_grams": (
                                item.weight_grams
                            ),

                            "dimensions": {
                                "length_cm": str(
                                    item.length_cm
                                ),
                                "width_cm": str(
                                    item.width_cm
                                ),
                                "height_cm": str(
                                    item.height_cm
                                ),
                            },
                        }
                        for item in package.items
                    ],

                    "rate_field": (
                        rate_field
                    ),

                    "rate": rate,

                    "amount_toman": (
                        amount_toman
                    ),
                }
            )

        return (
            total_amount_toman,
            package_breakdown,
        )

    # =========================================================
    # Quote
    # =========================================================

    def quote(
        self,
        *,
        method,
        destination_address,
        weight_grams=None,
        package_value_toman=0,
        packages=None,
        origin=None,
    ) -> ProviderQuote:
        """
        Quote نهایی Tipax.

        weight_grams:
            فقط برای سازگاری Interface عمومی نگه داشته شده.
            در Tipax جدید از ShippingPackageها استفاده می‌کنیم.

        package_value_toman:
            fallback برای حالت تک‌بسته‌ای.

        packages:
            لیست ShippingPackage ساخته‌شده توسط
            PackagingService.

        origin:
            اختیاری.
            اگر None باشد Default ShippingOrigin خوانده می‌شود.
        """

        self._validate_method(
            method
        )

        if packages is None:
            raise ShippingProviderConfigurationError(
                (
                    "TipaxProvider برای محاسبه قیمت "
                    "به ShippingPackageها نیاز دارد."
                )
            )

        packages = list(
            packages
        )

        if not packages:
            raise ShippingProviderConfigurationError(
                (
                    "هیچ Packageای برای "
                    "محاسبه قیمت Tipax وجود ندارد."
                )
            )

        # -------------------------
        # Origin
        # -------------------------

        origin = self._get_origin(
            origin
        )

        if not getattr(
            origin,
            "city_id",
            None,
        ):
            raise ShippingProviderConfigurationError(
                (
                    "شهر مبدا ارسال "
                    "مشخص نشده است."
                )
            )

        # -------------------------
        # Destination
        # -------------------------

        if destination_address is None:
            raise ShippingProviderConfigurationError(
                "آدرس مقصد مشخص نشده است."
            )

        if not getattr(
            destination_address,
            "city_id",
            None,
        ):
            raise ShippingProviderConfigurationError(
                (
                    "شهر مقصد ارسال "
                    "مشخص نشده است."
                )
            )

        # -------------------------
        # Settings
        # -------------------------

        settings_obj = (
            self._get_tipax_settings()
        )

        self._validate_tipax_settings(
            settings_obj
        )

        service_id = (
            self._get_service_id(
                method,
                settings_obj,
            )
        )

        # -------------------------
        # Provider city IDs
        # -------------------------

        origin_city_id = (
            self._get_tipax_city_id(
                origin.city
            )
        )

        destination_city_id = (
            self._get_tipax_city_id(
                destination_address.city
            )
        )

        # -------------------------
        # API calls
        # -------------------------

        try:
            services = (
                self._get_available_services(
                    origin_city_id=(
                        origin_city_id
                    ),
                    destination_city_id=(
                        destination_city_id
                    ),
                )
            )

            service_info = (
                self._find_service(
                    services=services,
                    service_id=service_id,
                )
            )

            payload = (
                self._build_pricing_payload(
                    packages=packages,

                    origin_city_id=(
                        origin_city_id
                    ),

                    destination_city_id=(
                        destination_city_id
                    ),

                    service_id=(
                        service_id
                    ),

                    settings_obj=(
                        settings_obj
                    ),

                    fallback_package_value_toman=(
                        package_value_toman
                    ),
                )
            )

            pricing_result = (
                self.client.pricing(
                    payload
                )
            )

        except TipaxAPIError as exc:
            raise ShippingProviderUnavailableError(
                (
                    "خطا در ارتباط با API تیپاکس: "
                    f"{exc}"
                )
            ) from exc

        # -------------------------
        # Parse pricing
        # -------------------------

        (
            total_amount_toman,
            package_breakdown,
        ) = (
            self._parse_pricing_result(
                pricing_result=(
                    pricing_result
                ),

                packages=packages,

                service_id=service_id,

                fallback_package_value_toman=(
                    package_value_toman
                ),
            )
        )

        # =====================================================
        # Provider snapshot data
        # =====================================================

        provider_data = {
            "provider": "TIPAX",

            # -----------------------------------------
            # Origin snapshot
            # -----------------------------------------

            "origin": {
                "shipping_origin_id": (
                    origin.pk
                ),

                "title": (
                    origin.title
                ),

                "province_id": (
                    origin.province_id
                ),

                "province_name": (
                    origin.province.name
                ),

                "city_id": (
                    origin.city_id
                ),

                "city_name": (
                    origin.city.name
                ),

                "provider_city_id": (
                    origin_city_id
                ),
            },

            # -----------------------------------------
            # Destination snapshot
            # -----------------------------------------

            "destination": {
                "city_id": (
                    destination_address
                    .city_id
                ),

                "city_name": (
                    destination_address
                    .city
                    .name
                ),

                "provider_city_id": (
                    destination_city_id
                ),
            },

            # -----------------------------------------
            # Service snapshot
            # -----------------------------------------

            "service_id": (
                service_id
            ),

            "service": (
                service_info
            ),

            # -----------------------------------------
            # Package snapshot
            # -----------------------------------------

            "package_count": len(
                packages
            ),

            "packages": (
                package_breakdown
            ),

            # -----------------------------------------
            # Pricing
            # -----------------------------------------

            "amount_toman": (
                total_amount_toman
            ),

            "pricing_response": (
                pricing_result
            ),
        }

        return ProviderQuote(
            amount_toman=(
                total_amount_toman
            ),

            provider_data=(
                provider_data
            ),
        )