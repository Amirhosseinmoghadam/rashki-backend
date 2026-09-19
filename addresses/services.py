from django.db import transaction

from addresses.models import Address


class AddressServiceError(Exception):
    pass


@transaction.atomic
def create_address(*, user, validated_data):
    addresses = (
        Address.objects
        .select_for_update()
        .filter(user=user)
    )

    has_addresses = addresses.exists()

    if not has_addresses:
        validated_data["is_default"] = True

    if validated_data.get("is_default") is True:
        addresses.filter(is_default=True).update(is_default=False)

    return Address.objects.create(
        user=user,
        **validated_data,
    )


@transaction.atomic
def update_address(*, address, validated_data):
    address = (
        Address.objects
        .select_for_update()
        .get(pk=address.pk)
    )

    user_addresses = (
        Address.objects
        .select_for_update()
        .filter(user=address.user)
    )

    requested_default = validated_data.get(
        "is_default",
        address.is_default,
    )

    if address.is_default and requested_default is False:
        raise AddressServiceError(
            "نمی‌توانید آدرس پیش‌فرض را بدون انتخاب آدرس جدید حذف کنید."
        )

    if requested_default is True:
        (
            user_addresses
            .filter(is_default=True)
            .exclude(pk=address.pk)
            .update(is_default=False)
        )

    for field, value in validated_data.items():
        setattr(address, field, value)

    address.save()
    return address


@transaction.atomic
def set_default_address(*, address):
    address = (
        Address.objects
        .select_for_update()
        .get(pk=address.pk)
    )

    (
        Address.objects
        .select_for_update()
        .filter(
            user=address.user,
            is_default=True,
        )
        .exclude(pk=address.pk)
        .update(is_default=False)
    )

    if not address.is_default:
        address.is_default = True
        address.save(
            update_fields=[
                "is_default",
                "updated_at",
            ]
        )

    return address


@transaction.atomic
def delete_address(*, address):
    address = (
        Address.objects
        .select_for_update()
        .get(pk=address.pk)
    )

    user = address.user
    was_default = address.is_default
    address.delete()

    if was_default:
        new_default = (
            Address.objects
            .select_for_update()
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )

        if new_default is not None:
            new_default.is_default = True
            new_default.save(
                update_fields=[
                    "is_default",
                    "updated_at",
                ]
            )
