from addresses.models import Address, City, Province


def get_provinces():
    return Province.objects.all().order_by("name")


def get_cities_for_province(*, province_id):
    return (
        City.objects
        .filter(province_id=province_id)
        .order_by("name")
    )


def get_user_addresses(*, user):
    return (
        Address.objects
        .filter(user=user)
        .select_related("province", "city")
        .order_by("-is_default", "-created_at")
    )


def get_user_address(*, user, pk):
    return (
        get_user_addresses(user=user)
        .filter(pk=pk)
        .first()
    )
