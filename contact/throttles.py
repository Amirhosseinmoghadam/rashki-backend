from rest_framework.throttling import (
    AnonRateThrottle,
)


# =========================================================
# Contact Request Throttle
# =========================================================


class ContactRequestThrottle(
    AnonRateThrottle
):
    """
    Rate limit public contact requests.

    Rate is configured in:

        REST_FRAMEWORK[
            "DEFAULT_THROTTLE_RATES"
        ]["contact"]
    """

    scope = "contact"