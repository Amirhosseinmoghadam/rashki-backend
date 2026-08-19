from rest_framework.throttling import AnonRateThrottle


class ContactRequestThrottle(AnonRateThrottle):
    scope = "contact"