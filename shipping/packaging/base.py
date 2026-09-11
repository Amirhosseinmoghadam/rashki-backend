from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ShippingPackageItem:
    product_id: int
    product_name: str
    quantity: int

    weight_grams: int

    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal


@dataclass(frozen=True)
class ShippingPackage:
    """
    مدل مستقل بسته‌بندی.

    این مدل هیچ وابستگی مستقیمی به Tipax ندارد.
    Providerها بعداً آن را به Payload خودشان تبدیل می‌کنند.
    """

    weight_grams: int

    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal

    items: tuple[ShippingPackageItem, ...]

    # ارزش واقعی کالا داخل این بسته.
    # PackagingService الزامی به دانستن آن ندارد.
    # Shipping/Checkout هنگام Quote آن را تزریق می‌کند.
    declared_value_toman: int | None = None

    provider_packing_id: int | None = None
    provider_packing_title: str = ""

    box_number: int | None = None

    pack_type: int | None = None
    package_content_id: int | None = None
    parcel_type_id: int | None = None

    metadata: dict = field(
        default_factory=dict,
    )

    @property
    def volume_cm3(self) -> Decimal:
        return (
            self.length_cm
            * self.width_cm
            * self.height_cm
        )