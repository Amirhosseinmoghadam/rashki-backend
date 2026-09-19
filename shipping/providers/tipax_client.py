from __future__ import annotations

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
)

import requests

from django.conf import settings
from django.core.cache import cache


# =========================================================
# Exceptions
# =========================================================


class TipaxAPIError(Exception):
    """
    Base exception for all Tipax API errors.
    """

    pass


class TipaxAuthenticationError(
    TipaxAPIError
):
    """
    Authentication / Token errors.
    """

    pass


class TipaxRequestError(
    TipaxAPIError
):
    """
    HTTP or business validation errors returned by Tipax.
    """

    pass


class TipaxIndeterminateError(
    TipaxRequestError
):
    """
    نتیجه یک عملیات Write در Tipax نامشخص است.

    مثال:
        درخواست Cancel ارسال شده،
        اما Timeout یا Network Error رخ داده است.

    در این وضعیت نمی‌دانیم:

        1. Request اصلاً به Tipax نرسیده است.

        یا:

        2. Tipax عملیات را انجام داده،
           ولی Response به سرور ما نرسیده است.

    بنابراین Retry خودکار برای چنین عملیاتی
    مجاز نیست.
    """

    pass


class TipaxConfigurationError(
    TipaxAPIError
):
    """
    Missing or invalid local Tipax configuration.
    """

    pass


# =========================================================
# Tipax Client
# =========================================================


class TipaxClient:
    """
    Client اصلی ارتباط با Tipax API.

    مسئولیت‌ها:

    - Login
    - Refresh Token
    - Bearer Authentication
    - Retry یک‌باره بعد از 401
    - Reference Data
    - Pricing
    - Order Creation
    - Tracking
    - Cancellation
    - Money conversion

    نکته مهم:

    برای عملیات Write حساس مثل Cancel می‌توان
    indeterminate_on_network_error=True ارسال کرد.

    در این حالت Timeout / Network Error به جای
    TipaxRequestError تبدیل به TipaxIndeterminateError
    می‌شود تا سیستم از Retry خودکار جلوگیری کند.
    """

    ACCESS_TOKEN_CACHE_KEY = (
        "shipping:tipax:access_token"
    )

    REFRESH_TOKEN_CACHE_KEY = (
        "shipping:tipax:refresh_token"
    )

    # Token را کمی زودتر از زمان واقعی
    # منقضی در نظر می‌گیریم.
    TOKEN_EXPIRY_SAFETY_SECONDS = 120

    DEFAULT_TOKEN_EXPIRES_SECONDS = 36000

    # =====================================================
    # Init
    # =====================================================

    def __init__(
        self,
    ):

        self.base_url = (
            getattr(
                settings,
                "TIPAX_BASE_URL",
                "https://omtestapi.tipax.ir",
            )
            .rstrip("/")
        )

        self.timeout = int(
            getattr(
                settings,
                "TIPAX_HTTP_TIMEOUT_SECONDS",
                20,
            )
        )

        self.session = (
            requests.Session()
        )

    # =====================================================
    # Settings Helpers
    # =====================================================

    @staticmethod
    def _setting(
        name,
        default=None,
    ):

        return getattr(
            settings,
            name,
            default,
        )

    def _path(
        self,
        setting_name,
        default,
    ):

        return self._setting(
            setting_name,
            default,
        )

    # =====================================================
    # URL
    # =====================================================

    def _url(
        self,
        path,
    ):
        """
        Build absolute Tipax URL.
        """

        path = str(
            path
            or ""
        ).strip()

        if not path:

            raise TipaxConfigurationError(
                "مسیر API تیپاکس تعریف نشده است."
            )

        if path.startswith(
            (
                "http://",
                "https://",
            )
        ):

            return path

        if not path.startswith(
            "/"
        ):

            path = (
                f"/{path}"
            )

        return (
            f"{self.base_url}"
            f"{path}"
        )

    # =====================================================
    # Recursive Value Finder
    # =====================================================

    def _find_value(
        self,
        payload,
        *keys,
    ):
        """
        پیدا کردن Key در Responseهای Nested.

        مثال:

        {
            "data": {
                "result": {
                    "accessToken": "..."
                }
            }
        }
        """

        wanted = {
            str(
                key
            ).lower()
            for key in keys
        }

        # -------------------------------------------------
        # Dict
        # -------------------------------------------------

        if isinstance(
            payload,
            dict,
        ):

            # First current level.
            for key, value in (
                payload.items()
            ):

                if (
                    str(
                        key
                    ).lower()
                    in wanted
                ):

                    return value

            # Then nested.
            for value in (
                payload.values()
            ):

                result = (
                    self._find_value(
                        value,
                        *keys,
                    )
                )

                if result is not None:

                    return result

        # -------------------------------------------------
        # List
        # -------------------------------------------------

        elif isinstance(
            payload,
            list,
        ):

            for item in payload:

                result = (
                    self._find_value(
                        item,
                        *keys,
                    )
                )

                if result is not None:

                    return result

        return None

    # =====================================================
    # Cache / Token Getters
    # =====================================================

    def _get_access_token(
        self,
    ):
        """
        اول Cache و بعد ENV/settings.
        """

        token = cache.get(
            self.ACCESS_TOKEN_CACHE_KEY
        )

        if not token:

            token = self._setting(
                "TIPAX_ACCESS_TOKEN",
                "",
            )

        if not token:

            return ""

        return str(
            token
        ).strip()

    def _get_refresh_token(
        self,
    ):
        """
        اول Cache و بعد ENV/settings.
        """

        token = cache.get(
            self.REFRESH_TOKEN_CACHE_KEY
        )

        if not token:

            token = self._setting(
                "TIPAX_REFRESH_TOKEN",
                "",
            )

        if not token:

            return ""

        return str(
            token
        ).strip()

    # =====================================================
    # Login Credentials
    # =====================================================

    def _has_login_credentials(
        self,
    ):

        return bool(
            self._setting(
                "TIPAX_USERNAME",
                "",
            )
            and
            self._setting(
                "TIPAX_PASSWORD",
                "",
            )
            and
            self._setting(
                "TIPAX_API_KEY",
                "",
            )
        )

    # =====================================================
    # Response Parser
    # =====================================================

    @staticmethod
    def _response_data(
        response,
    ):
        """
        Safe response parser.
        """

        if not response.content:

            return {}

        try:

            return response.json()

        except ValueError:

            text = (
                response.text
                or ""
            ).strip()

            if not text:

                return {}

            return {
                "raw": text,
            }

    # =====================================================
    # Flatten Validation Errors
    # =====================================================

    def _flatten_error_values(
        self,
        value,
    ):
        """
        ASP.NET / Tipax errors را به list[str]
        تبدیل می‌کند.
        """

        result = []

        if value is None:

            return result

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            if value:

                result.append(
                    value
                )

            return result

        if isinstance(
            value,
            (
                int,
                float,
                bool,
            ),
        ):

            result.append(
                str(
                    value
                )
            )

            return result

        if isinstance(
            value,
            dict,
        ):

            for nested_value in (
                value.values()
            ):

                result.extend(
                    self._flatten_error_values(
                        nested_value
                    )
                )

            return result

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):

            for item in value:

                result.extend(
                    self._flatten_error_values(
                        item
                    )
                )

            return result

        result.append(
            str(
                value
            )
        )

        return result

    # =====================================================
    # HTTP Error Message
    # =====================================================

    def _error_message(
        self,
        response,
        data,
    ):
        """
        خطای واقعی Tipax را نمایش می‌دهد.

        مثال:

        Tipax HTTP 400 |
        The PackageInputs field is required.
        """

        messages = [
            (
                f"Tipax HTTP "
                f"{response.status_code}"
            )
        ]

        if isinstance(
            data,
            dict,
        ):

            # ---------------------------------------------
            # Known message keys
            # ---------------------------------------------

            for key in (
                "message",
                "Message",
                "detail",
                "title",
                "error",
                "errorMessage",
            ):

                value = data.get(
                    key
                )

                if value:

                    messages.extend(
                        self._flatten_error_values(
                            value
                        )
                    )

            # ---------------------------------------------
            # ASP.NET validation errors
            # ---------------------------------------------

            if data.get(
                "errors"
            ):

                messages.extend(
                    self._flatten_error_values(
                        data.get(
                            "errors"
                        )
                    )
                )

            # ---------------------------------------------
            # Some Tipax APIs return messages
            # ---------------------------------------------

            if data.get(
                "messages"
            ):

                messages.extend(
                    self._flatten_error_values(
                        data.get(
                            "messages"
                        )
                    )
                )

            # Unknown structure.
            if len(
                messages
            ) == 1:

                raw = data.get(
                    "raw"
                )

                if raw:

                    messages.append(
                        str(
                            raw
                        )[:3000]
                    )

        elif data:

            messages.append(
                str(
                    data
                )[:3000]
            )

        # Remove duplicates while keeping order.
        unique_messages = []

        seen = set()

        for item in messages:

            item = str(
                item
            ).strip()

            if (
                item
                and
                item not in seen
            ):

                unique_messages.append(
                    item
                )

                seen.add(
                    item
                )

        return " | ".join(
            unique_messages
        )

    # =====================================================
    # Store Tokens
    # =====================================================

    def _store_tokens(
        self,
        data,
        *,
        fallback_refresh_token=None,
    ):
        """
        Access/Refresh Token را بدون ساختن
        self.access_token / self.refresh_token
        در Cache ذخیره می‌کند.

        Client کاملاً getter-based است.
        """

        if not isinstance(
            data,
            dict,
        ):

            raise TipaxAuthenticationError(
                (
                    "پاسخ احراز هویت Tipax "
                    "ساختار JSON معتبری ندارد."
                )
            )

        # =================================================
        # Access Token
        # =================================================

        access_token = (
            self._find_value(
                data,
                "accessToken",
                "access_token",
            )
        )

        if not access_token:

            raise TipaxAuthenticationError(
                (
                    "Tipax accessToken در پاسخ "
                    "وجود ندارد."
                )
            )

        access_token = str(
            access_token
        ).strip()

        # =================================================
        # Refresh Token
        # =================================================

        refresh_token = (
            self._find_value(
                data,
                "refreshToken",
                "refresh_token",
            )
        )

        if not refresh_token:

            refresh_token = (
                fallback_refresh_token
            )

        if refresh_token:

            refresh_token = str(
                refresh_token
            ).strip()

        # =================================================
        # Expiration
        # =================================================

        expires_in = (
            self._find_value(
                data,
                "expiresIn",
                "expires_in",
            )
        )

        try:

            expires_in = int(
                expires_in
            )

        except (
            TypeError,
            ValueError,
        ):

            expires_in = (
                self.DEFAULT_TOKEN_EXPIRES_SECONDS
            )

        access_timeout = max(
            (
                expires_in
                -
                self.TOKEN_EXPIRY_SAFETY_SECONDS
            ),
            60,
        )

        # =================================================
        # Cache
        # =================================================

        cache.set(
            self.ACCESS_TOKEN_CACHE_KEY,
            access_token,
            timeout=(
                access_timeout
            ),
        )

        if refresh_token:

            cache.set(
                self.REFRESH_TOKEN_CACHE_KEY,
                refresh_token,
                timeout=None,
            )

        return access_token

    # =====================================================
    # Clear Cached Tokens
    # =====================================================

    def clear_cached_tokens(
        self,
    ):

        cache.delete(
            self.ACCESS_TOKEN_CACHE_KEY
        )

        cache.delete(
            self.REFRESH_TOKEN_CACHE_KEY
        )

    # =====================================================
    # Login
    # =====================================================

    def login(
        self,
    ):
        """
        Login اولیه با:

        Username
        Password
        APIkey
        """

        username = self._setting(
            "TIPAX_USERNAME",
            "",
        )

        password = self._setting(
            "TIPAX_PASSWORD",
            "",
        )

        api_key = self._setting(
            "TIPAX_API_KEY",
            "",
        )

        if not (
            username
            and
            password
            and
            api_key
        ):

            raise TipaxAuthenticationError(
                (
                    "برای Login مجدد تیپاکس "
                    "TIPAX_USERNAME، "
                    "TIPAX_PASSWORD و "
                    "TIPAX_API_KEY باید در "
                    "تنظیمات/.env تعریف شده باشند."
                )
            )

        path = self._path(
            "TIPAX_TOKEN_PATH",
            "/api/OM/v3/Account/token",
        )

        payload = {
            "Username": username,
            "Password": password,
            "APIkey": api_key,
        }

        try:

            response = (
                self.session.post(
                    self._url(
                        path
                    ),
                    json=payload,
                    headers={
                        "Accept": (
                            "application/json"
                        ),
                    },
                    timeout=(
                        self.timeout
                    ),
                )
            )

        except requests.RequestException as exc:

            raise TipaxAuthenticationError(
                (
                    "خطا در اتصال به Login "
                    f"تیپاکس: {exc}"
                )
            ) from exc

        data = self._response_data(
            response
        )

        if not response.ok:

            raise TipaxAuthenticationError(
                self._error_message(
                    response,
                    data,
                )
            )

        return self._store_tokens(
            data
        )

    # =====================================================
    # Refresh Access Token
    # =====================================================

    def refresh_access_token(
        self,
    ):
        """
        Refresh Access Token.

        مهم:
        هیچ self.refresh_token یا self.access_token
        در این Client وجود ندارد.

        اگر Refresh Token نامعتبر باشد و Credentialهای
        اصلی وجود داشته باشند، Login جدید انجام می‌شود.
        """

        refresh_token = (
            self._get_refresh_token()
        )

        old_access_token = (
            self._get_access_token()
        )

        # =================================================
        # No Refresh Token
        # =================================================

        if not refresh_token:

            if self._has_login_credentials():

                return self.login()

            raise TipaxAuthenticationError(
                (
                    "Refresh Token تیپاکس وجود ندارد "
                    "و Credential لازم برای Login "
                    "مجدد نیز تعریف نشده است."
                )
            )

        path = self._path(
            "TIPAX_REFRESH_TOKEN_PATH",
            "/api/OM/v3/Account/RefreshToken",
        )

        payload = {
            "Token": (
                old_access_token
                or ""
            ),
            "refreshToken": (
                refresh_token
            ),
        }

        try:

            response = (
                self.session.post(
                    self._url(
                        path
                    ),
                    json=payload,
                    headers={
                        "Accept": (
                            "application/json"
                        ),
                    },
                    timeout=(
                        self.timeout
                    ),
                )
            )

        except requests.RequestException as exc:

            raise TipaxAuthenticationError(
                (
                    "خطا در اتصال به Refresh Token "
                    f"تیپاکس: {exc}"
                )
            ) from exc

        data = self._response_data(
            response
        )

        # =================================================
        # HTTP Refresh Failure
        # =================================================

        if not response.ok:

            if self._has_login_credentials():

                return self.login()

            raise TipaxAuthenticationError(
                self._error_message(
                    response,
                    data,
                )
            )

        # =================================================
        # HTTP 200 but no accessToken
        # =================================================

        try:

            return self._store_tokens(
                data,
                fallback_refresh_token=(
                    refresh_token
                ),
            )

        except TipaxAuthenticationError:

            if self._has_login_credentials():

                return self.login()

            raise

    # =====================================================
    # Ensure Access Token
    # =====================================================

    def _ensure_access_token(
        self,
    ):

        token = (
            self._get_access_token()
        )

        if token:

            return token

        if self._get_refresh_token():

            try:

                return (
                    self.refresh_access_token()
                )

            except TipaxAuthenticationError:

                if not (
                    self._has_login_credentials()
                ):

                    raise

        if self._has_login_credentials():

            return self.login()

        raise TipaxAuthenticationError(
            (
                "Access Token تیپاکس وجود ندارد "
                "و امکان Refresh/Login مجدد نیز "
                "وجود ندارد."
            )
        )

    # =====================================================
    # Generic HTTP Request
    # =====================================================

    def request(
        self,
        method,
        path,
        *,
        json=None,
        params=None,
        requires_auth=True,
        retry_auth=True,
        indeterminate_on_network_error=False,
    ):
        """
        Generic Tipax Request.

        اگر 401 دریافت شود:
        یک بار Refresh/Login انجام می‌شود
        و همان Request Retry می‌شود.

        indeterminate_on_network_error:

            False:
                Network Error یک TipaxRequestError
                معمولی است.

            True:
                Network Error در عملیات Write حساس
                نتیجه نامشخص ایجاد می‌کند و
                TipaxIndeterminateError می‌دهد.
        """

        headers = {
            "Accept": (
                "application/json"
            ),
        }

        # =================================================
        # Bearer Token
        # =================================================

        if requires_auth:

            token = (
                self._ensure_access_token()
            )

            headers[
                "Authorization"
            ] = (
                f"Bearer {token}"
            )

        url = self._url(
            path
        )

        # =================================================
        # HTTP Request
        # =================================================

        try:

            response = (
                self.session.request(
                    method=str(
                        method
                    ).upper(),
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                    timeout=(
                        self.timeout
                    ),
                )
            )

        except requests.RequestException as exc:

            # -------------------------------------------------
            # Sensitive Write Operation
            # -------------------------------------------------
            #
            # برای Cancel یا عملیات حساس مشابه:
            #
            # Timeout به معنای Failure قطعی نیست.
            #
            # ممکن است عملیات در Provider انجام شده باشد
            # ولی Response به ما نرسیده باشد.
            # -------------------------------------------------

            if indeterminate_on_network_error:

                raise TipaxIndeterminateError(
                    (
                        "نتیجه عملیات Tipax به دلیل "
                        "خطای ارتباطی نامشخص است و "
                        "نیاز به بررسی Provider دارد."
                    )
                ) from exc

            raise TipaxRequestError(
                (
                    "خطا در اتصال به API تیپاکس: "
                    f"{exc}"
                )
            ) from exc

        data = self._response_data(
            response
        )

        # =================================================
        # Unauthorized
        # =================================================

        if (
            response.status_code == 401
            and
            requires_auth
            and
            retry_auth
        ):

            cache.delete(
                self.ACCESS_TOKEN_CACHE_KEY
            )

            self.refresh_access_token()

            # Retry only once.
            #
            # مهم:
            # flag نتیجه نامشخص را نیز حفظ می‌کنیم.
            return self.request(
                method,
                path,
                json=json,
                params=params,
                requires_auth=(
                    requires_auth
                ),
                retry_auth=False,
                indeterminate_on_network_error=(
                    indeterminate_on_network_error
                ),
            )

        # =================================================
        # Other HTTP Errors
        # =================================================

        if not response.ok:

            raise TipaxRequestError(
                self._error_message(
                    response,
                    data,
                )
            )

        return data

    # =====================================================
    # Money Conversion
    # =====================================================

    def _amount_divisor(
        self,
    ):
        """
        اگر Tipax مبلغ را به تومان برگرداند:
            divisor = 1

        اگر Tipax مبلغ را به ریال برگرداند:
            divisor = 10
        """

        value = self._setting(
            "TIPAX_AMOUNT_DIVISOR_TO_TOMAN",
            1,
        )

        try:

            value = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            value = 1

        if value <= 0:

            value = 1

        return value

    def to_toman(
        self,
        provider_amount,
    ):
        """
        Tipax amount -> Toman.
        """

        try:

            amount = Decimal(
                str(
                    provider_amount
                )
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:

            raise TipaxRequestError(
                (
                    "مبلغ برگشتی Tipax "
                    "قابل تبدیل نیست."
                )
            ) from exc

        divisor = Decimal(
            self._amount_divisor()
        )

        result = (
            amount
            / divisor
        )

        return int(
            result.quantize(
                Decimal("1"),
                rounding=(
                    ROUND_HALF_UP
                ),
            )
        )

    def to_tipax_amount(
        self,
        toman_amount,
    ):
        """
        Toman -> Tipax provider amount.
        """

        try:

            amount = Decimal(
                str(
                    toman_amount
                )
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:

            raise TipaxRequestError(
                (
                    "مبلغ تومان قابل تبدیل "
                    "برای Tipax نیست."
                )
            ) from exc

        multiplier = Decimal(
            self._amount_divisor()
        )

        result = (
            amount
            * multiplier
        )

        return int(
            result.quantize(
                Decimal("1"),
                rounding=(
                    ROUND_HALF_UP
                ),
            )
        )

    # =====================================================
    # Reference Data
    # =====================================================

    def get_pack_content_rates(
        self,
    ):

        return self.request(
            "GET",
            self._path(
                "TIPAX_PACK_CONTENT_RATES_PATH",
                "/api/OM/v3/PackContentRates",
            ),
        )

    def get_packing_prices(
        self,
    ):

        return self.request(
            "GET",
            self._path(
                "TIPAX_PACKING_PRICES_PATH",
                "/api/OM/v3/PackingPrices",
            ),
        )

    def get_parcel_types(
        self,
    ):

        return self.request(
            "POST",
            self._path(
                "TIPAX_PARCEL_TYPES_PATH",
                "/api/OM/v3/ParcelType/Search",
            ),
            json={},
        )

    def get_payment_types(
        self,
    ):

        return self.request(
            "POST",
            self._path(
                "TIPAX_PAYMENT_TYPES_PATH",
                "/api/OM/v3/PaymentType/Search",
            ),
            json={},
        )

    def get_cities(
        self,
    ):

        return self.request(
            "GET",
            self._path(
                "TIPAX_CITIES_PATH",
                "/api/OM/v3/Cities",
            ),
        )

    def get_states(
            self,
    ):
        return self.request(
            "GET",
            self._path(
                "TIPAX_STATES_PATH",
                "/api/OM/v3/States",
            ),
        )

    def get_services_between_cities(
        self,
        *,
        source_city_id,
        destination_city_id,
    ):
        """
        دریافت سرویس‌های فعال Tipax بین دو شهر.

        Swagger:
            POST
            /api/OM/v3/Pricing/GetServicesBetweenCities
        """

        try:

            source_city_id = int(
                source_city_id
            )

            destination_city_id = int(
                destination_city_id
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise TipaxRequestError(
                (
                    "شناسه شهر مبدا یا مقصد "
                    "برای Tipax معتبر نیست."
                )
            ) from exc

        payload = {
            "sourceCityId": (
                source_city_id
            ),
            "destinationCityId": (
                destination_city_id
            ),
        }

        return self.request(
            "POST",
            self._path(
                "TIPAX_SERVICES_BETWEEN_CITIES_PATH",
                (
                    "/api/OM/v3/Pricing/"
                    "GetServicesBetweenCities"
                ),
            ),
            json=payload,
        )

    # =====================================================
    # Pricing
    # =====================================================

    def pricing(
        self,
        payload,
    ):
        """
        Pricing واقعی Tipax.
        """

        if not isinstance(
            payload,
            dict,
        ):

            raise TipaxRequestError(
                (
                    "Payload محاسبه قیمت "
                    "Tipax باید dict باشد."
                )
            )

        return self.request(
            "POST",
            self._path(
                "TIPAX_PRICING_PATH",
                "/api/OM/v3/Pricing",
            ),
            json=payload,
        )

    # =====================================================
    # Create Order
    # =====================================================

    def create_order(
        self,
        payload,
    ):
        """
        ثبت سفارش/مرسوله در Tipax.
        """

        if not isinstance(
            payload,
            dict,
        ):

            raise TipaxRequestError(
                (
                    "Payload ثبت سفارش Tipax "
                    "باید dict باشد."
                )
            )

        return self.request(
            "POST",
            self._path(
                "TIPAX_ORDERS_PATH",
                "/api/OM/v3/Orders",
            ),
            json=payload,
        )

    # =====================================================
    # Business Addresses
    # =====================================================

    def get_business_addresses(
        self,
        *,
        postal_code=None,
        page=None,
        page_size=None,
    ):
        """
        دریافت آدرس‌های کسب‌وکار ثبت‌شده
        برای حساب جاری Tipax.
        """

        params = {}

        if postal_code:

            params[
                "PostalCode"
            ] = str(
                postal_code
            ).strip()

        if page is not None:

            params[
                "Page"
            ] = int(
                page
            )

        if page_size is not None:

            params[
                "PageSize"
            ] = int(
                page_size
            )

        return self.request(
            "GET",
            self._path(
                "TIPAX_ADDRESSES_PATH",
                "/api/OM/v3/Addresses",
            ),
            params=(
                params
                or None
            ),
        )

    def create_business_address(
        self,
        payload,
    ):
        """
        ثبت آدرس کسب‌وکار جدید در Tipax.
        """

        if not isinstance(
            payload,
            dict,
        ):

            raise TipaxRequestError(
                (
                    "Payload آدرس Tipax "
                    "باید dict باشد."
                )
            )

        return self.request(
            "POST",
            self._path(
                "TIPAX_ADDRESSES_PATH",
                "/api/OM/v3/Addresses",
            ),
            json=payload,
        )

    # =====================================================
    # Create Order With Predefined Origin
    # =====================================================

    def create_order_with_predefined_origin(
        self,
        payload,
    ):
        """
        ثبت سفارش با مبدا از قبل تعریف‌شده.

        Swagger:
            POST
            /api/OM/v3/Orders/WithPreDefinedOrigin
        """

        if not isinstance(
            payload,
            dict,
        ):

            raise TipaxRequestError(
                (
                    "Payload ثبت سفارش Tipax "
                    "باید dict باشد."
                )
            )

        packages = payload.get(
            "packages"
        )

        if (
            not isinstance(
                packages,
                list,
            )
            or
            not packages
        ):

            raise TipaxRequestError(
                (
                    "برای ثبت سفارش Tipax "
                    "حداقل یک package لازم است."
                )
            )

        return self.request(
            "POST",
            self._path(
                "TIPAX_ORDER_PREDEFINED_ORIGIN_PATH",
                (
                    "/api/OM/v3/Orders/"
                    "WithPreDefinedOrigin"
                ),
            ),
            json=payload,
        )

    # =====================================================
    # Cancel Order
    # =====================================================

    def cancel_order(
        self,
        order_id,
    ):
        """
        لغو کل Order در Tipax.

        این یک عملیات Write حساس است.

        اگر Network Error رخ دهد، نتیجه را
        UNKNOWN در نظر می‌گیریم و نباید
        Retry خودکار انجام شود.
        """

        if not order_id:

            raise TipaxRequestError(
                "Tipax orderId الزامی است."
            )

        template = self._path(
            "TIPAX_CANCEL_ORDER_PATH",
            (
                "/api/OM/v3/Orders/"
                "CancelOrder/{order_id}"
            ),
        )

        path = template.format(
            order_id=(
                order_id
            )
        )

        return self.request(
            "POST",
            path,
            indeterminate_on_network_error=True,
        )

    # =====================================================
    # Brief Tracking
    # =====================================================

    def brief_tracking(
        self,
        tracking_code,
    ):

        if not tracking_code:

            raise TipaxRequestError(
                "کد رهگیری Tipax الزامی است."
            )

        template = self._path(
            "TIPAX_BRIEF_TRACKING_PATH",
            (
                "/api/OM/v3/Tracking/"
                "BriefTracking/{tracking_code}"
            ),
        )

        path = template.format(
            tracking_code=(
                tracking_code
            )
        )

        return self.request(
            "GET",
            path,
        )

    # =====================================================
    # Tracking By Order ID
    # =====================================================

    def track_by_order_id(
        self,
        order_id,
    ):

        if not order_id:

            raise TipaxRequestError(
                "Tipax orderId الزامی است."
            )

        template = self._path(
            "TIPAX_TRACK_BY_ORDER_PATH",
            "/api/OM/v3/Tracking/{order_id}",
        )

        path = template.format(
            order_id=(
                order_id
            )
        )

        return self.request(
            "GET",
            path,
        )

    # =====================================================
    # Parcels By Order ID
    # =====================================================

    def get_parcels_by_order_id(
        self,
        order_id,
    ):

        if not order_id:

            raise TipaxRequestError(
                "Tipax orderId الزامی است."
            )

        path = (
            "/api/OM/v3/Parcels/"
            f"GetByOrderId/{order_id}"
        )

        return self.request(
            "GET",
            path,
        )

    # =====================================================
    # Parcel Price Detail
    # =====================================================

    def get_parcel_price_detail(
        self,
        tracking_code,
    ):

        if not tracking_code:

            raise TipaxRequestError(
                "کد رهگیری Tipax الزامی است."
            )

        path = (
            "/api/OM/v3/Parcels/"
            "GetPriceDetailByTrackingCode/"
            f"{tracking_code}"
        )

        return self.request(
            "GET",
            path,
        )

    # =====================================================
    # Cancel Parcel
    # =====================================================

    def cancel_parcel(
        self,
        tracking_code,
    ):
        """
        ابطال یک Parcel مشخص با Tracking Code.

        Swagger:
            PUT
            /api/OM/v3/Parcels/Cancel/{trackingCode}

        این هم یک عملیات Write حساس است؛
        بنابراین Network Error نتیجه نامشخص دارد.
        """

        if not tracking_code:

            raise TipaxRequestError(
                "کد رهگیری Tipax الزامی است."
            )

        path = (
            "/api/OM/v3/Parcels/"
            f"Cancel/{tracking_code}"
        )

        return self.request(
            "PUT",
            path,
            indeterminate_on_network_error=True,
        )