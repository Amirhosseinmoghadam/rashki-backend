from django.conf import settings


class SMSConfig:
    """
    Central configuration for MeliPayamak SMS service.
    """

    @staticmethod
    def get_api_token() -> str:
        try:
            token = settings.MELIPAYAMAK["API_TOKEN"]
        except (AttributeError, KeyError):
            raise RuntimeError(
                "MELIPAYAMAK['API_TOKEN'] "
                "is not configured."
            )

        if not token:
            raise RuntimeError(
                "MELIPAYAMAK['API_TOKEN'] "
                "is not configured."
            )

        return token

    @staticmethod
    def get_default_from() -> str:
        try:
            sender = settings.MELIPAYAMAK["DEFAULT_FROM"]
        except (AttributeError, KeyError):
            raise RuntimeError(
                "MELIPAYAMAK['DEFAULT_FROM'] "
                "is not configured."
            )

        if not sender:
            raise RuntimeError(
                "MELIPAYAMAK['DEFAULT_FROM'] "
                "is not configured."
            )

        return str(sender)

    @classmethod
    def get(cls) -> dict:
        return {
            "API_TOKEN": cls.get_api_token(),
            "DEFAULT_FROM": cls.get_default_from(),
        }